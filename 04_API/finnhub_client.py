import sys
import os
import importlib
from dotenv import load_dotenv

# Add parent directory of internal finnhub package to sys.path
# finnhub package structure: 04_API/finnhub/finnhub/client.py
# Need to add 04_API/finnhub to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
finnhub_package_dir = os.path.join(os.path.dirname(__file__), 'finnhub')
if finnhub_package_dir not in sys.path:
    sys.path.insert(0, finnhub_package_dir)

import finnhub
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Use importlib to import validator
_validator_module = importlib.import_module('04_API.validator')
NewsValidator = _validator_module.NewsValidator


class FinnhubAPIClient:
    """Finnhub API Client"""
    
    def __init__(self, api_key: str = None, env_path: str = None, enable_validation: bool = True):
        """
        Initialize Finnhub API client
        
        Args:
            api_key: Finnhub API key (if not provided, read from .env)
            env_path: .env file path
            enable_validation: Whether to enable data validation (enabled by default)
        """
        # Load environment variables
        if env_path is None:
            env_path = os.path.join(project_root, '.env')
        
        print(f"🔍 Attempting to load .env file: {env_path}")
        load_dotenv(dotenv_path=env_path)
        
        # Initialize API client
        if api_key is None:
            api_key = os.environ.get("FINNHUB_API_KEY")
            if not api_key:
                raise EnvironmentError(f"FINNHUB_API_KEY not found in .env file! Path: {env_path}")
        
        self.client = finnhub.Client(api_key=api_key)
        self.enable_validation = enable_validation
    
    # ===================== Company Profile Related =====================
    def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company profile
        
        Args:
            symbol: Stock ticker (e.g., AAPL, MSFT)
        
        Returns:
            Company profile data dictionary, including country, currency, exchange, IPO date, market cap, etc.
        """
        try:
            data = self.client.company_profile2(symbol=symbol)
            if data:
                print(f"✅ Successfully retrieved information for {data.get('name')}")
            else:
                print(f"⚠️  No company data retrieved for {symbol}")
            return data
        except Exception as e:
            print(f"❌ Failed to get company info for {symbol}: {e}")
            return None
    
    # ===================== Company News Related =====================
    def get_company_news(self, symbol: str, _from: str, to: str, 
                        validate: bool = True, deduplicate: bool = True) -> List[Dict[str, Any]]:
        """
        Get company news
        
        Args:
            symbol: Stock ticker
            _from: Start date (YYYY-MM-DD)
            to: End date (YYYY-MM-DD)
            validate: Whether to validate data (enabled by default)
            deduplicate: Whether to deduplicate (enabled by default)
        
        Returns:
            News list, each news item includes id, category, datetime, headline, image, related, source, summary, url, etc.
        """
        try:
            news_list = self.client.company_news(symbol, _from=_from, to=to)
            print(f"✅ Successfully retrieved {len(news_list)} raw news items for {symbol}")
            
            # Data validation and deduplication
            if self.enable_validation and validate and news_list:
                # Validate
                valid_news = NewsValidator.validate_batch_news(news_list)
                print(f"✅ Validation passed: {len(valid_news)}/{len(news_list)} news items")
                
                # Deduplicate
                if deduplicate:
                    unique_news = NewsValidator.deduplicate_news(valid_news)
                    removed = len(valid_news) - len(unique_news)
                    if removed > 0:
                        print(f"✅ Deduplication complete: Removed {removed} duplicate news items")
                    return unique_news
                
                return valid_news
            
            return news_list
        except Exception as e:
            print(f"❌ Failed to get news for {symbol}: {e}")
            return []
    
    def get_recent_company_news(self, symbol: str, days: int = 30, 
                               validate: bool = True, deduplicate: bool = True) -> List[Dict[str, Any]]:
        """
        Get company news from last N days
        
        Args:
            symbol: Stock ticker
            days: Number of days (default 30 days)
            validate: Whether to validate data (enabled by default)
            deduplicate: Whether to deduplicate (enabled by default)
        
        Returns:
            News list
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return self.get_company_news(symbol, _from=start_date, to=end_date, 
                                    validate=validate, deduplicate=deduplicate)
    
    # ===================== Market News Related =====================
    def get_market_news(self, category: str = "general", min_id: int = 0,
                       validate: bool = True, deduplicate: bool = True) -> List[Dict[str, Any]]:
        """
        Get market news
        
        Args:
            category: News category (general, forex, crypto, merger, etc.)
            min_id: Minimum news ID (for pagination)
            validate: Whether to validate data (enabled by default)
            deduplicate: Whether to deduplicate (enabled by default)
        
        Returns:
            News list
        """
        try:
            news_list = self.client.general_news(category, min_id=min_id)
            print(f"✅ Successfully retrieved {len(news_list)} raw market news items for {category} category")
            
            # Data validation and deduplication
            if self.enable_validation and validate and news_list:
                # Validate
                valid_news = NewsValidator.validate_batch_news(news_list)
                print(f"✅ Validation passed: {len(valid_news)}/{len(news_list)} news items")
                
                # Deduplicate
                if deduplicate:
                    unique_news = NewsValidator.deduplicate_news(valid_news)
                    removed = len(valid_news) - len(unique_news)
                    if removed > 0:
                        print(f"✅ Deduplication complete: Removed {removed} duplicate news items")
                    return unique_news
                
                return valid_news
            
            return news_list
        except Exception as e:
            print(f"❌ Failed to get {category} market news: {e}")
            return []


# ===================== Usage Example =====================
if __name__ == "__main__":
    # Initialize client (validation enabled by default)
    client = FinnhubAPIClient()
    
    # 1. Get company profile
    print("\n" + "="*60)
    print("Get Company Profile")
    print("="*60)
    profile = client.get_company_profile("AAPL")
    if profile:
        print(f"Company Name: {profile.get('name')}")
        print(f"Exchange: {profile.get('exchange')}")
        print(f"Market Cap: {profile.get('marketCapitalization')}")
    
    # 2. Get company news (last 30 days, with automatic validation and deduplication)
    print("\n" + "="*60)
    print("Get Company News (with validation and deduplication)")
    print("="*60)
    company_news = client.get_recent_company_news("AAPL", days=30)
    if company_news:
        print(f"Finally obtained {len(company_news)} valid news items")
        for i, news in enumerate(company_news[:3], 1):  # Only show first 3
            print(f"\nNews {i}:")
            print(f"  ID: {news.get('id')}")
            print(f"  Headline: {news.get('headline')}")
            print(f"  Source: {news.get('source')}")
