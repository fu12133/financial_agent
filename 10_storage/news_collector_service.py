"""
Financial News Collector - Windows Service Version
Runs as a background service, automatically executes at 3 AM daily
"""
import sys
import os
import logging
import importlib
from datetime import datetime
import time
import schedule
import threading
import signal

# Add project root directory to path (key: two levels up to project root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules
_pipeline_module = importlib.import_module('08_pipeline.news_processor')
FinancialNewsProcessor = _pipeline_module.FinancialNewsProcessor

_api_module = importlib.import_module('04_API.finnhub_client')
FinnhubAPIClient = _api_module.FinnhubAPIClient

_config_module = importlib.import_module('05_config.settings')
Config = _config_module.Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(project_root, 'news_collector_service.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NewsCollectorService:
    """News collection service"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
    
    def fetch_and_store_news(self):
        """Fetch and store news"""
        logger.info("\n" + "="*70)
        logger.info("🚀 Starting popular company news collection task")
        logger.info(f"⏰ Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)

        try:
            # Initialize API client
            api_client = FinnhubAPIClient()
            
            # Read popular company list from configuration file
            hot_companies = Config.POPULAR_TICKERS
            
            # Set time range (last 7 days)
            days = 7
            
            all_news = []
            
            for symbol in hot_companies:
                logger.info(f"\n📡 Fetching news for {symbol}...")
                
                try:
                    company_news = api_client.get_recent_company_news(
                        symbol=symbol, 
                        days=days,
                        validate=True,
                        deduplicate=True
                    )
                    
                    if company_news:
                        logger.info(f"✅ {symbol}: Retrieved {len(company_news)} valid news items")
                        
                        for news in company_news:
                            if 'ticker' not in news and 'related' not in news:
                                news['ticker'] = symbol
                        
                        all_news.extend(company_news)
                    else:
                        logger.warning(f"⚠️  {symbol}: No news retrieved")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to fetch news for {symbol}: {e}")
                    continue
            
            logger.info(f"\n{'='*70}")
            logger.info(f"📊 Total news retrieved: {len(all_news)}")
            logger.info(f"{'='*70}")
            
            if not all_news:
                logger.warning("⚠️  No news retrieved, task ended")
                return
            
            # Initialize news processor
            processor = FinancialNewsProcessor(device='cuda')
            
            # Process news and ingest into database
            processor.process_and_insert(
                all_news, 
                recreate_collection=False,
                batch_size=50
            )
            
            logger.info(f"\n✅ Successfully wrote {len(all_news)} news items to Milvus database")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}", exc_info=True)
    
    def start(self):
        """Start service"""
        if self.is_running:
            logger.warning("⚠️  Service already running")
            return
        
        self.is_running = True
        logger.info("="*70)
        logger.info("📅 Starting news collection service")
        logger.info(f"⏰ Scheduled task: Daily at 03:00 AM")
        logger.info("="*70)
        
        # Set scheduled task
        schedule.every().day.at("03:00").do(self.fetch_and_store_news)
        
        logger.info("✅ Scheduled task configured")
        logger.info("💡 Service running in background, press Ctrl+C to stop\n")
        
        # Register signal handler (graceful exit)
        def signal_handler(sig, frame):
            logger.info("\n🛑 Received stop signal")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run scheduler in separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Main thread keeps running
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 User interrupt, stopping service...")
            self.stop()
    
    def _run_scheduler(self):
        """Run scheduler (in thread)"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)
    
    def stop(self):
        """Stop service"""
        if not self.is_running:
            return
        
        logger.info("🛑 Stopping service...")
        self.is_running = False
        
        # Wait for scheduler thread to end (non-blocking)
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            try:
                self.scheduler_thread.join(timeout=5)
                if self.scheduler_thread.is_alive():
                    logger.warning("⚠️  Scheduler thread did not stop within 5 seconds")
            except Exception as e:
                logger.error(f"❌ Error stopping thread: {e}")
        
        logger.info("✅ Service stopped")


if __name__ == "__main__":
    service = NewsCollectorService()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--run-now':
        logger.info("🔄 Executing task immediately...\n")
        service.fetch_and_store_news()
    else:
        logger.info("Tip: Use --run-now parameter to execute task immediately\n")
    
    # Start service
    service.start()
