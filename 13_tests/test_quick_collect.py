"""
Quick Run News Collection Test
"""
import sys
from pathlib import Path

# Add project root directory
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("="*70)
print("🧪 News Collection Script Quick Test")
print("="*70)

# Test import
print("\n📋 Test 1: Module Import")
print("-"*40)
try:
    import importlib
    _collect = importlib.import_module('14_scripts.collect_news')
    print("✅ collect_news.py imported successfully")

    _quick = importlib.import_module('14_scripts.quick_collect')
    print("✅ quick_collect.py imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test configuration
print("\n📋 Test 2: Configuration Check")
print("-"*40)
try:
    INDUSTRIES = _collect.INDUSTRY_COMPANIES
    CATEGORIES = _collect.GENERAL_NEWS_CATEGORIES

    print(f"✅ Number of industries: {len(INDUSTRIES)}")
    print(f"✅ General categories: {len(CATEGORIES)}")

    total_companies = sum(len(info['tickers']) for info in INDUSTRIES.values())
    print(f"✅ Total companies: {total_companies}")
except Exception as e:
    print(f"❌ Configuration check failed: {e}")
    sys.exit(1)

# Test initialization
print("\n📋 Test 3: Collector Initialization")
print("-"*40)
try:
    collector = _collect.NewsCollector(days=1)
    print(f"✅ Collector initialized successfully")
    print(f"   Time range: {collector.start_date} to {collector.end_date}")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✅ Quick test passed!")
print("="*70)
print("\n💡 Run full test:")
print("   pytest 13_tests/test_collect_news.py -v")
