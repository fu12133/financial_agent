"""
Scheduled News Collection Scheduler
Uses APScheduler to implement scheduled collection
"""
import sys
import importlib
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Use importlib to import
_collect_module = importlib.import_module('14_scripts.collect_news')
NewsCollector = _collect_module.NewsCollector

_quick_module = importlib.import_module('14_scripts.quick_collect')
quick_update = _quick_module.quick_update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scheduled_full_collection():
    """Execute full collection on schedule (daily at 2 AM)"""
    logger.info("\n⏰ Executing scheduled full collection...")
    try:
        collector = NewsCollector(days=7)
        collector.collect_all()
        logger.info("✅ Scheduled full collection completed")
    except Exception as e:
        logger.error(f"❌ Scheduled full collection failed: {e}")


def scheduled_quick_update():
    """Execute quick update on schedule (every 6 hours)"""
    logger.info("\n⏰ Executing scheduled quick update...")
    try:
        quick_update(days=1)
        logger.info("✅ Scheduled quick update completed")
    except Exception as e:
        logger.error(f"❌ Scheduled quick update failed: {e}")


def main():
    """Start scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="News collection scheduled scheduler")
    parser.add_argument("--test", action="store_true", help="Test mode: execute once immediately then exit")

    args = parser.parse_args()

    if args.test:
        logger.info("🧪 Test mode: Execute one full collection")
        scheduled_full_collection()
        logger.info("✅ Test completed")
        return

    scheduler = BlockingScheduler()

    # Execute full collection daily at 2 AM
    scheduler.add_job(
        scheduled_full_collection,
        CronTrigger(hour=2, minute=0),
        id='daily_full_collection',
        name='Daily Full News Collection',
        replace_existing=True
    )

    # Execute quick update every 6 hours
    scheduler.add_job(
        scheduled_quick_update,
        CronTrigger(hour='*/6', minute=0),
        id='hourly_quick_update',
        name='Quick Update Every 6 Hours',
        replace_existing=True
    )

    logger.info("🕒 News collection scheduler started")
    logger.info("   - Daily full collection: Every day at 2:00 AM")
    logger.info("   - Quick update: Every 6 hours")
    logger.info("   - Press Ctrl+C to stop")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("\n🛑 Scheduler stopped")


if __name__ == "__main__":
    import argparse
    main()
