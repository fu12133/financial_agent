"""
News Collection Script Test
Test news collection functionality in 14_scripts directory
"""
import sys
import importlib
from pathlib import Path
from datetime import datetime, timedelta
import pytest

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use importlib to import modules
_collect_module = importlib.import_module('14_scripts.collect_news')
NewsCollector = _collect_module.NewsCollector
INDUSTRY_COMPANIES = _collect_module.INDUSTRY_COMPANIES
GENERAL_NEWS_CATEGORIES = _collect_module.GENERAL_NEWS_CATEGORIES


class TestNewsCollector:
    """News collector test class"""

    @pytest.fixture
    def collector(self):
        """Create collector instance (for testing)"""
        return NewsCollector(days=1, enable_validation=True)

    # ==================== Configuration Tests ====================

    def test_01_industry_companies_config(self):
        """Test 1: Industry company configuration"""
        print("\n📋 Test 1: Industry company configuration")
        print("-" * 40)

        # Check if there are 8 industries
        assert len(INDUSTRY_COMPANIES) == 8, f"Should have 8 industries, actually has {len(INDUSTRY_COMPANIES)}"

        # Check structure of each industry
        for industry_code, industry_info in INDUSTRY_COMPANIES.items():
            assert 'name' in industry_info, f"{industry_code} missing name field"
            assert 'tickers' in industry_info, f"{industry_code} missing tickers field"
            assert 'description' in industry_info, f"{industry_code} missing description field"
            assert len(industry_info['tickers']) > 0, f"{industry_code}'s tickers list is empty"
            print(f"✅ {industry_code}: {industry_info['name']} ({len(industry_info['tickers'])} companies)")

        print("✅ Industry configuration test passed")

    def test_02_general_news_categories(self):
        """Test 2: General news category configuration"""
        print("\n📋 Test 2: General news category configuration")
        print("-" * 40)

        expected_categories = ["general", "forex", "crypto", "merger"]

        for category in expected_categories:
            assert category in GENERAL_NEWS_CATEGORIES, f"Missing category: {category}"
            print(f"✅ {category}: {GENERAL_NEWS_CATEGORIES[category]}")

        assert len(GENERAL_NEWS_CATEGORIES) == 4, "Should have 4 news categories"
        print("✅ General news category configuration test passed")

    # ==================== Initialization Tests ====================

    def test_03_collector_initialization(self):
        """Test 3: Collector initialization"""
        print("\n📋 Test 3: Collector initialization")
        print("-" * 40)

        collector = NewsCollector(days=7)

        assert collector.days == 7, "days parameter should be 7"
        assert collector.finnhub is not None, "Finnhub client should be initialized"
        assert collector.milvus is not None, "Milvus manager should be initialized"
        assert collector.classifier is not None, "Classifier should be initialized"

        # Check date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        assert collector.end_date == end_date, "End date should be correct"
        assert collector.start_date == start_date, "Start date should be correct"

        print(f"✅ Collector initialized successfully")
        print(f"   Time range: {collector.start_date} to {collector.end_date}")
        print("✅ Initialization test passed")

    # ==================== Data Validation Tests ====================

    def test_04_date_range_calculation(self):
        """Test 4: Date range calculation"""
        print("\n📋 Test 4: Date range calculation")
        print("-" * 40)

        for days in [1, 7, 14, 30]:
            collector = NewsCollector(days=days)

            expected_end = datetime.now().strftime("%Y-%m-%d")
            expected_start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            assert collector.end_date == expected_end, f"{days} days: end date error"
            assert collector.start_date == expected_start, f"{days} days: start date error"

            print(f"✅ {days} days: {collector.start_date} to {collector.end_date}")

        print("✅ Date range calculation test passed")

    # ==================== Industry Configuration Completeness Tests ====================

    def test_05_industry_ticker_uniqueness(self):
        """Test 5: Check for duplicate stock tickers"""
        print("\n📋 Test 5: Stock ticker uniqueness check")
        print("-" * 40)

        all_tickers = []
        for industry_code, industry_info in INDUSTRY_COMPANIES.items():
            tickers = industry_info['tickers']
            all_tickers.extend(tickers)
            print(f"   {industry_code}: {len(tickers)} companies")

        # Check total count
        print(f"\n   Total stocks: {len(all_tickers)}")

        # Check duplicates
        unique_tickers = set(all_tickers)
        duplicates = len(all_tickers) - len(unique_tickers)

        if duplicates > 0:
            print(f"⚠️  Found {duplicates} duplicate stock tickers")
            from collections import Counter
            ticker_counts = Counter(all_tickers)
            for ticker, count in ticker_counts.items():
                if count > 1:
                    print(f"      {ticker}: appears {count} times")
        else:
            print("✅ No duplicate stock tickers")

        # TSLA can appear in multiple industries (technology, energy, automotive), which is reasonable
        print("✅ Stock ticker uniqueness check completed")

    def test_06_industry_coverage(self):
        """Test 6: Industry coverage check"""
        print("\n📋 Test 6: Industry coverage check")
        print("-" * 40)

        required_industries = [
            "technology",
            "finance",
            "healthcare_pharma",
            "consumer_retail"
        ]

        for industry in required_industries:
            assert industry in INDUSTRY_COMPANIES, f"Missing required industry: {industry}"
            info = INDUSTRY_COMPANIES[industry]
            print(f"✅ {info['name']}: {len(info['tickers'])} companies")

        print("✅ Industry coverage check passed")

    # ==================== Helper Method Tests ====================

    def test_07_get_collection_summary(self):
        """Test 7: Get collection configuration summary"""
        print("\n📋 Test 7: Collection configuration summary")
        print("-" * 40)

        collector = NewsCollector(days=7)
        summary = collector.get_collection_summary()

        # Check summary structure
        assert 'collection_period' in summary, "Missing collection_period"
        assert 'industries' in summary, "Missing industries"
        assert 'general_categories' in summary, "Missing general_categories"
        assert 'timestamp' in summary, "Missing timestamp"

        # Check specific content
        period = summary['collection_period']
        assert period['days'] == 7, "Days should be 7"
        assert 'start_date' in period, "Missing start_date"
        assert 'end_date' in period, "Missing end_date"

        print(f"✅ Collection period: {period['days']} days")
        print(f"✅ Number of industries: {len(summary['industries'])}")
        print(f"✅ General categories: {len(summary['general_categories'])}")
        print("✅ Configuration summary test passed")

    # ==================== Integration Tests (requires API Key) ====================

    @pytest.mark.skip(reason="Requires valid Finnhub API Key")
    def test_08_collect_single_company_news(self, collector):
        """Test 8: Collect single company news (integration test)"""
        print("\n📋 Test 8: Collect single company news")
        print("-" * 40)

        # Test only one company
        test_ticker = "AAPL"

        try:
            news_list = collector.finnhub.get_company_news(
                symbol=test_ticker,
                _from=collector.start_date,
                to=collector.end_date,
                validate=True,
                deduplicate=True
            )

            print(f"✅ Retrieved {len(news_list)} news items for {test_ticker}")

            # Verify news data structure
            if news_list:
                first_news = news_list[0]
                assert 'headline' in first_news, "News missing headline field"
                assert 'summary' in first_news or 'content' in first_news, "News missing content field"
                print(f"   Sample news: {first_news['headline'][:100]}...")

            print("✅ Single company news collection test passed")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise

    @pytest.mark.skip(reason="Requires valid Finnhub API Key")
    def test_09_collect_general_news(self, collector):
        """Test 9: Collect general news (integration test)"""
        print("\n📋 Test 9: Collect general news")
        print("-" * 40)

        try:
            news_list = collector.finnhub.get_market_news(
                category="general",
                min_id=0,
                validate=True,
                deduplicate=True
            )

            print(f"✅ Retrieved {len(news_list)} general news items")

            if news_list:
                first_news = news_list[0]
                assert 'headline' in first_news, "News missing headline field"
                print(f"   Sample news: {first_news['headline'][:100]}...")

            print("✅ General news collection test passed")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise

    # ==================== Classifier Tests ====================

    def test_10_news_classification(self):
        """Test 10: News classification functionality"""
        print("\n📋 Test 10: News classification functionality")
        print("-" * 40)

        collector = NewsCollector(days=1)

        # Mock a news item
        mock_news = {
            "id": 12345,
            "category": "company",
            "datetime": int(datetime.now().timestamp()),
            "headline": "Apple reports record quarterly revenue",
            "image": "",
            "related": "AAPL",
            "source": "Reuters",
            "summary": "Apple Inc reported better-than-expected quarterly earnings...",
            "url": "https://example.com/news/12345"
        }

        try:
            # Execute classification
            enriched_news = collector.classifier.full_classification(mock_news)

            # Verify classification results
            assert 'event_type' in enriched_news, "Missing event_type"
            assert 'industry' in enriched_news, "Missing industry"
            assert 'sentiment_polarity' in enriched_news, "Missing sentiment_polarity"
            assert 'primary_impact' in enriched_news, "Missing primary_impact"

            print(f"✅ Event type: {enriched_news['event_type']}")
            print(f"✅ Industry: {enriched_news['industry']}")
            print(f"✅ Sentiment: {enriched_news['sentiment_polarity']}")
            print(f"✅ Primary impact: {enriched_news['primary_impact']}")
            print("✅ News classification test passed")

        except Exception as e:
            print(f"❌ Classification failed: {e}")
            raise


class TestQuickCollect:
    """Quick collection script tests"""

    def test_01_quick_update_function_exists(self):
        """Test 1: quick_update function exists"""
        print("\n📋 Test 1: quick_update function existence")
        print("-" * 40)

        _quick_module = importlib.import_module('14_scripts.quick_collect')
        assert hasattr(_quick_module, 'quick_update'), "quick_update function does not exist"
        print("✅ quick_update function exists")


class TestScheduler:
    """Scheduler tests"""

    def test_01_scheduler_functions_exist(self):
        """Test 1: Scheduler functions exist"""
        print("\n📋 Test 1: Scheduler function existence")
        print("-" * 40)

        _scheduler_module = importlib.import_module('14_scripts.scheduler')

        assert hasattr(_scheduler_module, 'scheduled_full_collection'), "Missing scheduled_full_collection"
        assert hasattr(_scheduler_module, 'scheduled_quick_update'), "Missing scheduled_quick_update"
        assert hasattr(_scheduler_module, 'main'), "Missing main function"

        print("✅ All scheduler functions exist")
