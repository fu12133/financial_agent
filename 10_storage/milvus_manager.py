"""
Milvus Vector Database Manager
"""
import sys
import os
import json
import logging
import importlib
from typing import List, Dict, Optional, Tuple
from pymilvus import MilvusClient, DataType

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import config
_config_module = importlib.import_module('05_config.settings')
Config = _config_module.Config

logger = logging.getLogger(__name__)


class MilvusManager:
    """Milvus vector database operation wrapper"""

    def __init__(self, uri: str = None, collection_name: str = None):
        self.uri = uri or Config.MILVUS_URI
        self.collection_name = collection_name or Config.COLLECTION_NAME
        self.dimension = Config.VECTOR_DIMENSION
        
        logger.info(f"🔌 Connecting to Milvus: {self.uri}")
        try:
            self.client = MilvusClient(self.uri)
            logger.info("✅ Milvus connection successful")
        except Exception as e:
            logger.error(f"❌ Milvus connection failed: {e}")
            logger.error("💡 Please ensure Milvus service is running")
            logger.error("💡 Start command: docker run -d --name milvus-standalone -p 19530:19530 milvusdb/milvus:latest milvus run standalone")
            raise

    def init_collection(self, recreate: bool = False):
        """Initialize or recreate collection"""
        logger.info(f"📦 Checking collection: {self.collection_name}")
        
        if self.client.has_collection(self.collection_name):
            if recreate:
                logger.warning(f"🗑️  Deleting existing collection: {self.collection_name}")
                self.client.drop_collection(self.collection_name)
                logger.info(f"✅ Collection deleted")
            else:
                logger.info(f"✅ Collection {self.collection_name} already exists")
                return

        logger.info(f"🔨 Creating new collection: {self.collection_name}")
        schema = self.client.create_schema(
            auto_id=False,
            enable_dynamic_field=True
        )

        # Basic fields
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=self.dimension)

        # News metadata
        schema.add_field("ticker", DataType.VARCHAR, max_length=20)
        schema.add_field("headline", DataType.VARCHAR, max_length=1000)
        schema.add_field("summary", DataType.VARCHAR, max_length=5000)
        schema.add_field("url", DataType.VARCHAR, max_length=500)
        schema.add_field("source", DataType.VARCHAR, max_length=100)
        schema.add_field("publish_time", DataType.INT64)

        # Layer 1: Event classification
        schema.add_field("event_type", DataType.VARCHAR, max_length=50)
        schema.add_field("event_confidence", DataType.FLOAT)

        # Layer 2: Industry classification
        schema.add_field("industry", DataType.VARCHAR, max_length=50)
        schema.add_field("main_entity", DataType.VARCHAR, max_length=20)
        schema.add_field("industry_confidence", DataType.FLOAT)

        # Layer 3: Sentiment classification
        schema.add_field("sentiment_polarity", DataType.VARCHAR, max_length=20)
        schema.add_field("sentiment_intensity", DataType.VARCHAR, max_length=20)
        schema.add_field("sentiment_confidence", DataType.FLOAT)

        # Layer 4: Business impact
        schema.add_field("primary_impact", DataType.VARCHAR, max_length=50)
        schema.add_field("business_impacts", DataType.VARCHAR, max_length=200)

        logger.info("📊 Creating vector index...")
        # Create index
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            metric_type="COSINE",
            index_type="IVF_FLAT",
            params={"nlist": 128}
        )

        logger.info("🏗️  Creating collection...")
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )

        logger.info("📥 Loading collection into memory...")
        self.client.load_collection(self.collection_name)
        logger.info(f"✅ Collection {self.collection_name} created successfully (with four-layer classification fields)")

    def insert_batch(self, data: List[Dict]):
        """Batch insert data"""
        try:
            self.client.insert(self.collection_name, data)
            logger.info(f"✅ Successfully inserted {len(data)} records")
        except Exception as e:
            logger.error(f"❌ Insertion failed: {e}")
            raise

    def insert_news(self, news_data: Dict) -> bool:
        """
        Insert single news record
        
        Args:
            news_data: News data dictionary containing all fields
            
        Returns:
            Whether insertion was successful
        """
        try:
            # Build insert data, ensure all required fields exist
            insert_data = {
                "id": news_data.get("id", hash(news_data.get("headline", "")) % 1000000),
                "vector": news_data.get("vector", [0.0] * self.dimension),
                "ticker": str(news_data.get("ticker", news_data.get("related", "")))[:20],
                "headline": str(news_data.get("headline", ""))[:1000],
                "summary": str(news_data.get("summary", news_data.get("content", "")))[:5000],
                "url": str(news_data.get("url", ""))[:500],
                "source": str(news_data.get("source", ""))[:100],
                "publish_time": int(news_data.get("datetime", news_data.get("publish_time", 0))),
                
                # Layer 1: Event classification
                "event_type": str(news_data.get("event_type", "unknown"))[:50],
                "event_confidence": float(news_data.get("event_confidence", 0.0)),
                
                # Layer 2: Industry classification
                "industry": str(news_data.get("industry", "unknown"))[:50],
                "main_entity": str(news_data.get("main_entity", news_data.get("ticker", "")))[:20],
                "industry_confidence": float(news_data.get("industry_confidence", 0.0)),
                
                # Layer 3: Sentiment classification
                "sentiment_polarity": str(news_data.get("sentiment_polarity", "neutral"))[:20],
                "sentiment_intensity": str(news_data.get("sentiment_intensity", "moderate"))[:20],
                "sentiment_confidence": float(news_data.get("sentiment_confidence", 0.0)),
                
                # Layer 4: Business impact
                "primary_impact": str(news_data.get("primary_impact", "unknown"))[:50],
                "business_impacts": str(news_data.get("business_impacts", "[]"))[:200]
            }
            
            # Insert data
            self.client.insert(self.collection_name, [insert_data])
            logger.debug(f"✅ Successfully inserted news: {insert_data['headline'][:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to insert news: {e}")
            logger.error(f"   News data: {news_data.get('headline', 'N/A')}")
            return False

    def check_duplicate(self, news_id: int, vector: List[float]) -> Tuple[bool, Optional[int]]:
        """Check for duplicate news"""
        res = self.client.search(
            collection_name=self.collection_name,
            data=[vector],
            filter=f"id != {news_id}",
            limit=1,
            output_fields=["id"],
            params={"metric_type": "COSINE"}
        )

        if res[0] and len(res[0]) > 0 and res[0][0]["distance"] >= Config.DUPLICATE_THRESHOLD:
            return True, res[0][0]["entity"]["id"]
        return False, None

    def search_with_filters(self, query_vector: List[float],
                           event_type: str = "",
                           industry: str = "",
                           sentiment: str = "",
                           primary_impact: str = "",
                           limit: int = None,
                           threshold: float = None) -> List[Dict]:
        """Multi-dimensional filtered search"""
        limit = limit or Config.SEARCH_LIMIT
        threshold = threshold or Config.SEARCH_THRESHOLD

        filters = []
        if event_type:
            filters.append(f'event_type == "{event_type}"')
        if industry:
            filters.append(f'industry == "{industry}"')
        if sentiment:
            filters.append(f'sentiment_polarity == "{sentiment}"')
        if primary_impact:
            filters.append(f'primary_impact == "{primary_impact}"')

        filter_expr = " and ".join(filters) if filters else ""

        res = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            filter=filter_expr,
            limit=limit,
            output_fields=[
                "id", "ticker", "headline", "summary", "url", "source",
                "event_type", "industry", "sentiment_polarity", "sentiment_intensity",
                "primary_impact", "business_impacts"
            ],
            params={"metric_type": "COSINE", "params": {"nprobe": 10}}
        )

        results = []
        for hit in res[0]:
            if hit["distance"] >= threshold:
                result = hit["entity"]
                result["similarity"] = round(hit["distance"], 4)
                results.append(result)

        return results

    def drop_collection(self):
        """Drop collection"""
        if self.client.has_collection(self.collection_name):
            self.client.drop_collection(self.collection_name)
            logger.info(f"🗑️  Collection {self.collection_name} dropped")

    def get_statistics(self) -> Dict:
        """Get collection statistics"""
        try:
            stats = self.client.get_collection_stats(self.collection_name)
            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}