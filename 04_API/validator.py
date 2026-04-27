from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
import re


class NewsValidator:
    """News data validator - Adapted for Finnhub API"""

    # Invalid keywords list (news containing these keywords will be filtered)
    INVALID_KEYWORDS = [
        "spam",
        "advertisement",
        "promotion",
        "casino",
        "gambling",
    ]

    # Finnhub API required fields list
    REQUIRED_FIELDS = ["id", "headline", "url", "datetime"]

    @classmethod
    def validate_single_news(cls, news_data: Dict) -> tuple[bool, str]:
        """
        Validate single news item (Finnhub API format)

        Args:
            news_data: News data dictionary (from Finnhub API)

        Returns:
            (is_valid, error_message)
        """
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if not news_data.get(field):
                return False, f"Missing required field: {field}"

        # Validate URL format
        url = news_data.get("url", "")
        if not cls._is_valid_url(url):
            return False, f"Invalid URL format: {url}"

        # Validate headline length
        headline = news_data.get("headline", "")
        if len(headline) < 5:
            return False, f"Headline too short: {headline}"

        if len(headline) > 500:
            return False, f"Headline too long: {len(headline)} characters"

        # Check for invalid keywords
        if cls._contains_invalid_keywords(headline):
            return False, "Contains invalid keywords"

        # Validate publish time (Finnhub uses Unix timestamp)
        datetime_ts = news_data.get("datetime")
        if not cls._is_valid_timestamp(datetime_ts):
            return False, f"Invalid publish time: {datetime_ts}"

        # Validate source (if exists)
        source = news_data.get("source", "")
        if source and len(source) > 100:
            return False, f"Source field too long: {len(source)} characters"

        return True, ""

    @classmethod
    def validate_batch_news(cls, news_list: List[Dict]) -> List[Dict]:
        """
        Batch validate news data

        Args:
            news_list: News data list (from Finnhub API)

        Returns:
            List of validated news items
        """
        valid_news = []

        for news in news_list:
            is_valid, error_msg = cls.validate_single_news(news)

            if is_valid:
                valid_news.append(news)
            else:
                logger.debug(f"News validation failed: {error_msg} | {news.get('headline', '')[:50]}")

        logger.info(
            f"Batch validation complete: {len(valid_news)}/{len(news_list)} news items passed validation"
        )

        return valid_news

    @classmethod
    def deduplicate_news(cls, news_list: List[Dict]) -> List[Dict]:
        """
        Remove duplicate news (based on ID or URL)

        Args:
            news_list: News data list

        Returns:
            Deduplicated news list
        """
        seen_ids = set()
        unique_news = []

        for news in news_list:
            news_id = news.get("id")
            url = news.get("url", "")

            # Prioritize ID for deduplication, use URL if no ID
            identifier = news_id if news_id else url

            if identifier and identifier not in seen_ids:
                seen_ids.add(identifier)
                unique_news.append(news)

        removed_count = len(news_list) - len(unique_news)
        if removed_count > 0:
            logger.info(f"Deduplication complete, removed {removed_count} duplicate news items")

        return unique_news

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:[\w-]+\.)+[\w-]+'  # domain
            r'(?:\:[0-9]+)?'  # optional port
            r'(?:/[^\s]*)?$'  # path
        )
        return bool(url_pattern.match(url))

    @staticmethod
    def _is_valid_timestamp(ts) -> bool:
        """Validate Unix timestamp format (used by Finnhub API)"""
        try:
            if not isinstance(ts, (int, float)):
                return False
            
            # Check if timestamp is within reasonable range (2000-01-01 to 2030-01-01)
            if ts < 946684800 or ts > 1893456000:
                return False
            
            # Try to convert to datetime
            datetime.fromtimestamp(ts)
            return True
        except (ValueError, TypeError, OSError):
            return False

    @classmethod
    def _contains_invalid_keywords(cls, text: str) -> bool:
        """Check if contains invalid keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in cls.INVALID_KEYWORDS)
