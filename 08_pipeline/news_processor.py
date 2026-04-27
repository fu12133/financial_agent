"""
Financial News Processing Pipeline - Main Process Orchestration
"""
import sys
import os
import logging
import json
import importlib
from datetime import datetime
from typing import List, Dict, Optional

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules
_embedding_module = importlib.import_module('08_pipeline.embedding')
EmbeddingEngine = _embedding_module.EmbeddingEngine

_classifier_module = importlib.import_module('08_pipeline.classifier')
AdvancedNewsClassifier = _classifier_module.AdvancedNewsClassifier

_storage_module = importlib.import_module('10_storage.milvus_manager')
MilvusManager = _storage_module.MilvusManager

_config_module = importlib.import_module('05_config.settings')
Config = _config_module.Config

logger = logging.getLogger(__name__)


class FinancialNewsProcessor:
    """
    Financial News Intelligent Processing Pipeline

    Process:
    Finnhub API → Data Validation → BGE-M3 Vectorization → Deduplication Check →
    Four-Layer Classification & Tagging → Milvus Ingestion
    """

    def __init__(self, device: str = None):
        logger.info("=" * 70)
        logger.info("🚀 Initializing Financial News Processing Pipeline")
        logger.info("=" * 70)

        # Use specified device (CUDA or CPU)
        self.embedding_engine = EmbeddingEngine(device=device)
        self.classifier = AdvancedNewsClassifier()
        self.vector_db = MilvusManager()

        self.stats = {
            "total_processed": 0,
            "duplicates_removed": 0,
            "successfully_ingested": 0,
            "errors": 0
        }

    def process_and_insert(self, news_list: List[Dict],
                          batch_size: int = None,
                          recreate_collection: bool = False):
        """
        Process news and ingest into database (with four-layer classification)

        Args:
            news_list: News list
            batch_size: Batch processing size
            recreate_collection: Whether to recreate collection
        """
        batch_size = batch_size or Config.BATCH_SIZE

        logger.info("=" * 70)
        logger.info("Starting financial news processing (four-layer classification system)")
        logger.info("=" * 70)

        logger.info("📦 Initializing Milvus collection...")
        self.vector_db.init_collection(recreate=recreate_collection)
        logger.info("✅ Milvus collection ready")

        insert_data = []
        processed_count = 0

        for idx, news_item in enumerate(news_list, 1):
            try:
                logger.info(f"\n📰 Processing news [{idx}/{len(news_list)}]: {news_item.get('headline', '')[:60]}...")
                
                news_id = news_item.get("id")
                if not news_id:
                    logger.warning("⚠️  News missing ID, skipping")
                    continue

                headline = news_item.get("headline", "")
                summary = news_item.get("summary", "") or ""

                logger.info("   🔢 Generating vector...")
                vector = self.embedding_engine.encode_news(headline, summary)
                logger.info(f"   ✅ Vector generation complete (dimensions: {len(vector)})")

                logger.info("   🔍 Checking for duplicates...")
                is_dup, dup_id = self.vector_db.check_duplicate(news_id, vector)
                if is_dup:
                    logger.info(f"   ⚠️  Duplicate news found (ID: {dup_id}), skipping")
                    self.stats["duplicates_removed"] += 1
                    continue
                logger.info("   ✅ No duplicates")

                logger.info("   🏷️  Executing four-layer classification...")
                enriched_news = self.classifier.full_classification(news_item)
                logger.info(f"   ✅ Classification complete: {enriched_news.get('event_type')} | {enriched_news.get('industry')} | {enriched_news.get('sentiment_polarity')}")

                insert_data.append({
                    "id": news_id,
                    "vector": vector,
                    "ticker": enriched_news.get("ticker", "") or enriched_news.get("related", ""),
                    "headline": headline,
                    "summary": summary,
                    "url": news_item.get("url", ""),
                    "source": news_item.get("source", ""),
                    "publish_time": news_item.get("datetime", 0),

                    "event_type": enriched_news.get("event_type"),
                    "event_confidence": enriched_news.get("event_confidence"),

                    "industry": enriched_news.get("industry"),
                    "main_entity": enriched_news.get("main_entity"),
                    "industry_confidence": enriched_news.get("industry_confidence"),

                    "sentiment_polarity": enriched_news.get("sentiment_polarity"),
                    "sentiment_intensity": enriched_news.get("sentiment_intensity"),
                    "sentiment_confidence": enriched_news.get("sentiment_confidence"),

                    "primary_impact": enriched_news.get("primary_impact"),
                    "business_impacts": json.dumps(enriched_news.get("business_impacts", []))
                })

                processed_count += 1
                logger.info(f"   💾 Added to insertion queue")

                if len(insert_data) >= batch_size:
                    logger.info(f"\n📤 Batch inserting {len(insert_data)} records to Milvus...")
                    self.vector_db.insert_batch(insert_data)
                    self.stats["successfully_ingested"] += len(insert_data)
                    logger.info(f"Progress: [{idx}/{len(news_list)}] Processed {processed_count}, removed {self.stats['duplicates_removed']} duplicates")
                    insert_data = []

            except Exception as e:
                logger.error(f"❌ Error processing news {news_item.get('id')}: {e}", exc_info=True)
                self.stats["errors"] += 1
                continue

        if insert_data:
            logger.info(f"\n📤 Batch inserting remaining {len(insert_data)} records to Milvus...")
            self.vector_db.insert_batch(insert_data)
            self.stats["successfully_ingested"] += len(insert_data)

        self.stats["total_processed"] = len(news_list)
        self._print_report()

    def _print_report(self):
        """Print processing report"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 Processing Complete Report")
        logger.info("=" * 70)
        logger.info(f"📥 Total processed: {self.stats['total_processed']}")
        logger.info(f"✅ Successfully ingested: {self.stats['successfully_ingested']}")
        logger.info(f"🔄 Duplicates removed: {self.stats['duplicates_removed']}")
        logger.info(f"❌ Errors: {self.stats['errors']}")

        if self.stats['total_processed'] > 0:
            ingestion_rate = self.stats['successfully_ingested'] / self.stats['total_processed'] * 100
            logger.info(f"📈 Ingestion rate: {ingestion_rate:.2f}%")

        logger.info("=" * 70)

    def advanced_search(self, query_text: str,
                       event_type: str = "",
                       industry: str = "",
                       sentiment: str = "",
                       primary_impact: str = "",
                       limit: int = None) -> List[Dict]:
        """Advanced search: support multi-dimensional filtering"""
        query_vector = self.embedding_engine.encode_news(query_text, "")

        results = self.vector_db.search_with_filters(
            query_vector=query_vector,
            event_type=event_type,
            industry=industry,
            sentiment=sentiment,
            primary_impact=primary_impact,
            limit=limit
        )

        logger.info(f"🔍 Found {len(results)} related news items")
        return results