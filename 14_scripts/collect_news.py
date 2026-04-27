"""
News Collection Script - Collect industry news from Finnhub and store in Milvus
Supports two modes:
1. General News: Get market-wide news (by category)
2. Company News: Get news from leading companies in various industries
"""
import sys
import os
import importlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use importlib to import modules starting with numbers
_finnhub_module = importlib.import_module('04_API.finnhub_client')
FinnhubAPIClient = _finnhub_module.FinnhubAPIClient

_classifier_module = importlib.import_module('08_pipeline.classifier')
AdvancedNewsClassifier = _classifier_module.AdvancedNewsClassifier

_milvus_module = importlib.import_module('10_storage.milvus_manager')
MilvusManager = _milvus_module.MilvusManager


# ==================== Industry & Company Mapping Configuration ====================

# Industry and leading company mapping (select representative companies for each industry)
INDUSTRY_COMPANIES = {
    "technology": {
        "name": "Technology Industry",
        "tickers": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMD", "INTC", "ORCL", "CRM", "ADBE"],
        "description": "Including software, hardware, semiconductors, cloud computing, AI, etc."
    },
    "finance": {
        "name": "Finance Industry",
        "tickers": ["JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "SCHW", "AXP", "USB"],
        "description": "Including banking, investment, insurance, asset management, etc."
    },
    "healthcare_pharma": {
        "name": "Healthcare & Pharmaceuticals",
        "tickers": ["JNJ", "PFE", "MRNA", "ABBV", "TMO", "UNH", "LLY", "MRK", "ABT", "DHR"],
        "description": "Including pharmaceuticals, biotechnology, medical devices, healthcare services, etc."
    },
    "consumer_retail": {
        "name": "Consumer Retail",
        "tickers": ["AMZN", "WMT", "NKE", "SBUX", "MCD", "TGT", "HD", "LOW", "COST", "BABA"],
        "description": "Including e-commerce, retail, dining, consumer goods, etc."
    },
    "energy_utilities": {
        "name": "Energy & Utilities",
        "tickers": ["XOM", "CVX", "NEE", "TSLA", "COP", "SLB", "EOG", "PXD", "MPC", "VLO"],
        "description": "Including oil, natural gas, renewable energy, electricity, etc."
    },
    "automotive_manufacturing": {
        "name": "Automotive & Manufacturing",
        "tickers": ["TSLA", "F", "GM", "BA", "CAT", "GE", "HON", "MMM", "DE", "EMR"],
        "description": "Including automotive, aviation, industrial manufacturing, machinery, etc."
    },
    "real_estate": {
        "name": "Real Estate",
        "tickers": ["AMT", "PLD", "CCI", "EQIX", "PSA", "SPG", "O", "WELL", "DLR", "SBAC"],
        "description": "Including REITs, real estate development, property management, etc."
    },
    "telecommunications": {
        "name": "Telecommunications",
        "tickers": ["T", "VZ", "TMUS", "CHTR", "CMCSA", "DIS", "NFLX", "PARA", "WBD", "FOXA"],
        "description": "Including telecom operators, media, entertainment, etc."
    }
}

# Finnhub General News Category Mapping
GENERAL_NEWS_CATEGORIES = {
    "general": "General News",
    "forex": "Forex Market",
    "crypto": "Cryptocurrency",
    "merger": "Mergers & Acquisitions"
}


class NewsCollector:
    """News Collector"""

    def __init__(self, days: int = 7, enable_validation: bool = True):
        """
        Initialize news collector

        Args:
            days: How many days of recent news to collect
            enable_validation: Whether to enable data validation
        """
        self.days = days
        self.finnhub = FinnhubAPIClient(enable_validation=enable_validation)
        self.milvus = MilvusManager()
        self.classifier = AdvancedNewsClassifier()

        # Calculate date range
        self.end_date = datetime.now().strftime("%Y-%m-%d")
        self.start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        logger.info(f"📅 Collection time range: {self.start_date} to {self.end_date}")

    def collect_general_news(self, category: str = "general", limit: int = 50) -> int:
        """
        Collect general news (General News)

        Args:
            category: News category (general/forex/crypto/merger)
            limit: Maximum collection count

        Returns:
            Number of successfully inserted news items
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"📰 Starting general news collection: {GENERAL_NEWS_CATEGORIES.get(category, category)}")
        logger.info(f"{'='*70}")

        try:
            # Get general news
            news_list = self.finnhub.get_market_news(
                category=category,
                min_id=0,
                validate=True,
                deduplicate=True
            )

            if not news_list:
                logger.warning(f"⚠️  No news retrieved for {category} category")
                return 0

            logger.info(f"✅ Retrieved {len(news_list)} raw news items")

            # Limit quantity
            if limit and len(news_list) > limit:
                news_list = news_list[:limit]
                logger.info(f"📊 Limited to first {limit} news items")

            # Classify and store
            inserted_count = 0
            for i, news in enumerate(news_list, 1):
                try:
                    # Four-layer classification
                    enriched_news = self.classifier.full_classification(news)

                    # Add metadata
                    enriched_news['collection_type'] = 'general_news'
                    enriched_news['news_category'] = category
                    enriched_news['collected_at'] = datetime.now().isoformat()

                    # Insert into Milvus
                    success = self.milvus.insert_news(enriched_news)
                    if success:
                        inserted_count += 1

                    if i % 10 == 0:
                        logger.info(f"  Progress: {i}/{len(news_list)}, Inserted: {inserted_count}")

                except Exception as e:
                    logger.error(f"  ❌ Failed to process news item {i}: {e}")
                    continue

            logger.info(f"✅ General news collection complete: Inserted {inserted_count}/{len(news_list)} items")
            return inserted_count

        except Exception as e:
            logger.error(f"❌ Failed to collect general news: {e}")
            return 0

    def collect_industry_company_news(self, industry: str = None) -> int:
        """
        Collect news from leading companies in industries

        Args:
            industry: Specify industry name, None to collect all industries

        Returns:
            Number of successfully inserted news items
        """
        industries_to_collect = [industry] if industry else list(INDUSTRY_COMPANIES.keys())

        total_inserted = 0

        for ind in industries_to_collect:
            if ind not in INDUSTRY_COMPANIES:
                logger.warning(f"⚠️  Unknown industry: {ind}")
                continue

            industry_info = INDUSTRY_COMPANIES[ind]
            industry_name = industry_info['name']
            tickers = industry_info['tickers']

            logger.info(f"\n{'='*70}")
            logger.info(f"🏭 Starting {industry_name} ({ind}) news collection")
            logger.info(f"   Company count: {len(tickers)}")
            logger.info(f"   Company list: {', '.join(tickers[:5])}..." if len(tickers) > 5 else f"   Company list: {', '.join(tickers)}")
            logger.info(f"{'='*70}")

            industry_inserted = 0

            for ticker in tickers:
                try:
                    logger.info(f"\n  📊 Collecting news for {ticker}...")

                    # Get company news
                    news_list = self.finnhub.get_company_news(
                        symbol=ticker,
                        _from=self.start_date,
                        to=self.end_date,
                        validate=True,
                        deduplicate=True
                    )

                    if not news_list:
                        logger.info(f"    ⚠️  No news for {ticker}")
                        continue

                    logger.info(f"    ✅ Retrieved {len(news_list)} news items")

                    # Classify and store
                    for news in news_list:
                        try:
                            # Four-layer classification
                            enriched_news = self.classifier.full_classification(news)

                            # Add metadata
                            enriched_news['collection_type'] = 'company_news'
                            enriched_news['industry_focus'] = ind
                            enriched_news['collected_at'] = datetime.now().isoformat()

                            # Insert into Milvus
                            success = self.milvus.insert_news(enriched_news)
                            if success:
                                industry_inserted += 1

                        except Exception as e:
                            logger.error(f"    ❌ Failed to process news: {e}")
                            continue

                    # Avoid API rate limits
                    import time
                    time.sleep(0.5)

                except Exception as e:
                    logger.error(f"  ❌ Failed to collect news for {ticker}: {e}")
                    continue

            logger.info(f"\n✅ {industry_name} collection complete: Inserted {industry_inserted} news items")
            total_inserted += industry_inserted

        return total_inserted

    def collect_all(self, include_general: bool = True, include_companies: bool = True):
        """
        Collect all news

        Args:
            include_general: Whether to include general news
            include_companies: Whether to include company news
        """
        logger.info("\n" + "="*70)
        logger.info("🚀 Starting comprehensive news collection")
        logger.info("="*70)

        stats = {
            "general_news": 0,
            "company_news": 0,
            "total": 0
        }

        start_time = datetime.now()

        # 1. Collect general news
        if include_general:
            for category in GENERAL_NEWS_CATEGORIES.keys():
                count = self.collect_general_news(category=category, limit=30)
                stats["general_news"] += count

        # 2. Collect industry company news
        if include_companies:
            stats["company_news"] = self.collect_industry_company_news()

        # Statistics
        stats["total"] = stats["general_news"] + stats["company_news"]
        elapsed = (datetime.now() - start_time).total_seconds()

        logger.info("\n" + "="*70)
        logger.info("📊 Collection statistics")
        logger.info("="*70)
        logger.info(f"✅ General news: {stats['general_news']} items")
        logger.info(f"✅ Company news: {stats['company_news']} items")
        logger.info(f"✅ Total: {stats['total']} items")
        logger.info(f"⏱️  Elapsed time: {elapsed:.2f} seconds")
        logger.info("="*70)

        return stats

    def get_collection_summary(self) -> Dict[str, Any]:
        """
        Get collection configuration summary

        Returns:
            Configuration information dictionary
        """
        return {
            "collection_period": {
                "start_date": self.start_date,
                "end_date": self.end_date,
                "days": self.days
            },
            "industries": {
                ind: {
                    "name": info["name"],
                    "company_count": len(info["tickers"]),
                    "tickers": info["tickers"]
                }
                for ind, info in INDUSTRY_COMPANIES.items()
            },
            "general_categories": list(GENERAL_NEWS_CATEGORIES.keys()),
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Financial news collection tool")
    parser.add_argument("--days", type=int, default=7, help="Collect recent news for how many days (default: 7)")
    parser.add_argument("--industry", type=str, default=None,
                       help="Specify industry to collect (default: all industries)")
    parser.add_argument("--mode", type=str, default="all",
                       choices=["all", "general", "companies"],
                       help="Collection mode: all/general/companies (default: all)")
    parser.add_argument("--no-validation", action="store_true",
                       help="Disable data validation")

    args = parser.parse_args()

    # Create collector
    collector = NewsCollector(
        days=args.days,
        enable_validation=not args.no_validation
    )

    # Display configuration
    logger.info("\n📋 Collection configuration:")
    summary = collector.get_collection_summary()
    logger.info(f"   Time range: {summary['collection_period']['days']} days")
    logger.info(f"   Industry count: {len(summary['industries'])}")
    logger.info(f"   General categories: {', '.join(summary['general_categories'])}")

    # Execute collection
    if args.mode == "all":
        collector.collect_all(
            include_general=True,
            include_companies=True
        )
    elif args.mode == "general":
        collector.collect_all(
            include_general=True,
            include_companies=False
        )
    elif args.mode == "companies":
        if args.industry:
            collector.collect_industry_company_news(industry=args.industry)
        else:
            collector.collect_all(
                include_general=False,
                include_companies=True
            )

    logger.info("\n🎉 Collection task complete！")


if __name__ == "__main__":
    main()
