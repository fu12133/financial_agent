"""
Quick News Collection Script - For daily incremental updates
Only collects news from the last 1-3 days, faster speed
"""
import sys
import importlib
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use importlib to import
_collect_module = importlib.import_module('14_scripts.collect_news')
NewsCollector = _collect_module.NewsCollector

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def quick_update(days: int = 1):
    """
    Quick news update

    Args:
        days: Collection days (default 1 day)
    """
    logger.info(f"\n🚀 Starting quick news update (last {days} day(s))")

    collector = NewsCollector(days=days)

    # Only collect news from key industries
    key_industries = ["technology", "finance", "healthcare_pharma"]

    total = 0
    for industry in key_industries:
        count = collector.collect_industry_company_news(industry=industry)
        total += count

    # Collect general news
    general_count = collector.collect_general_news(category="general", limit=20)
    total += general_count

    logger.info(f"\n✅ Quick update completed: Collected {total} news items in total")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Quick news update tool")
    parser.add_argument("--days", type=int, default=1, help="Collection days (default: 1)")

    args = parser.parse_args()
    quick_update(days=args.days)
