"""
Intent recognition module - Understand user query intent and extract key information
"""
import logging
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Intent Type Enumeration"""
    COMPANY_ANALYSIS = "company_analysis"           # Company analysis
    INDUSTRY_ANALYSIS = "industry_analysis"         # Industry analysis
    NEWS_QUERY = "news_query"                       # News query
    STOCK_COMPARISON = "stock_comparison"           # Stock comparison
    MARKET_TREND = "market_trend"                   # Market trend
    SENTIMENT_ANALYSIS = "sentiment_analysis"       # Sentiment analysis
    WATCHLIST_MANAGE = "watchlist_manage"           # Watchlist management
    MEMORY_QUERY = "memory_query"                   # Memory query
    PREFERENCE_QUERY = "preference_query"           # Investment preference query
    REPORT_GENERATE = "report_generate"             # Report generation
    GENERAL_CHAT = "general_chat"                   # General chat
    UNKNOWN = "unknown"                             # Unknown intent


@dataclass
class ExtractedEntity:
    """Extracted entity"""
    entity_type: str                    # Entity type (ticker/company/time/etc)
    value: str                          # Entity value
    confidence: float = 1.0            # Confidence level


@dataclass
class IntentResult:
    """Intent recognition result"""
    intent_type: IntentType             # Intent type
    confidence: float                   # Confidence level (0-1)
    entities: List[ExtractedEntity] = field(default_factory=list)  # Extracted entities
    parameters: Dict[str, any] = field(default_factory=dict)       # Additional parameters
    raw_query: str = ""                 # Original query
    fallback_message: str = ""          # Fallback message (when intent is UNKNOWN)

    def get_tickers(self) -> List[str]:
        """Get all stock tickers"""
        return [e.value for e in self.entities if e.entity_type == 'ticker']

    def get_companies(self) -> List[str]:
        """Get all company names"""
        return [e.value for e in self.entities if e.entity_type == 'company']

    def get_industries(self) -> List[str]:
        """Get all industry names"""
        return [e.value for e in self.entities if e.entity_type == 'industry']

    def get_time_range(self) -> Optional[str]:
        """Get time range"""
        time_entities = [e for e in self.entities if e.entity_type == 'time']
        return time_entities[0].value if time_entities else None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
            "entities": [
                {"type": e.entity_type, "value": e.value, "confidence": e.confidence}
                for e in self.entities
            ],
            "parameters": self.parameters,
            "raw_query": self.raw_query,
            "fallback_message": self.fallback_message
        }


class IntentRecognizer:
    """
    Intent recognizer
    - Based on rules and keyword matching
    - Supports extension to LLM-enhanced version
    """

    def __init__(self):
        """Initialize intent recognizer"""
        # Intent keyword mapping
        self.intent_keywords = {
            IntentType.COMPANY_ANALYSIS: [
                'analyze', 'evaluate', 'financial', 'earnings', 'revenue', 'profit'
            ],
            IntentType.INDUSTRY_ANALYSIS: [
                'industry', 'sector', 
                'technology industry', 'finance industry', 'healthcare industry', 'consumer industry',
                'energy industry', 'automotive industry', 'real estate industry', 'telecommunications industry'
            ],
            IntentType.NEWS_QUERY: [
                'news', 'message', 'information', 'report', 'headline',
                'recent', 'latest', 'today'
            ],
            IntentType.STOCK_COMPARISON: [
                'compare', 'comparison', 'vs', 'versus', 'and', 'with',
                'difference', 'which is better'
            ],
            IntentType.MARKET_TREND: [
                'trend', 'movement', 'market', 'index', 'rise', 'fall'
            ],
            IntentType.SENTIMENT_ANALYSIS: [
                'sentiment', 'emotion', 'optimistic', 'pessimistic',
                'positive', 'negative', 'bullish', 'bearish'
            ],
            IntentType.WATCHLIST_MANAGE: [
                'watch', 'add', 'remove',
                'favorite', 'list'
            ],
            IntentType.MEMORY_QUERY: [
                'history', 'before', 'remember',
                'last time', 'once'
            ],
            IntentType.PREFERENCE_QUERY: [
                'preference', 'like', 'preference settings', 'my preferences',
                'investment preference'
            ],
            IntentType.REPORT_GENERATE: [
                'report', 'generate', 'create',
                'document', 'summary'
            ]
        }

        # Common company ticker mapping (expandable)
        self.company_ticker_map = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL', 'alphabet': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META', 'facebook': 'META',
            'nvidia': 'NVDA',
            'jpmorgan': 'JPM',
            'bank of america': 'BAC',
            'walmart': 'WMT',
            'alibaba': 'BABA',
            'tencent': '0700.HK',
        }

        # Industry name mapping
        self.industry_map = {
            'technology': 'technology',
            'finance': 'finance',
            'healthcare': 'healthcare_pharma',
            'health': 'healthcare_pharma',
            'consumer': 'consumer_retail',
            'retail': 'consumer_retail',
            'energy': 'energy_utilities',
            'automotive': 'automotive_manufacturing',
            'real estate': 'real_estate',
            'telecom': 'telecommunications'
        }

        # Stock ticker regex pattern
        self.ticker_pattern = re.compile(r'\b([A-Z]{1,5})\b')

        # Time expression patterns
        self.time_patterns = {
            'recent_days': re.compile(r'(\d+)\s*days?'),
            'recent_weeks': re.compile(r'(\d+)\s*weeks?'),
            'recent_months': re.compile(r'(\d+)\s*months?'),
            'today': re.compile(r'today'),
            'yesterday': re.compile(r'yesterday'),
            'this_week': re.compile(r'this week'),
            'this_month': re.compile(r'this month'),
        }

        logger.info("✅ Intent recognizer initialized successfully")

    def recognize(self, query: str) -> IntentResult:
        """
        Recognize user intent

        Args:
            query: User query text

        Returns:
            Intent recognition result
        """
        logger.info(f"🔍 Recognizing intent: {query}")

        # 1. Extract entities
        entities = self._extract_entities(query)

        # 2. Classify intent type
        intent_type, confidence = self._classify_intent(query)

        # 3. Extract parameters
        parameters = self._extract_parameters(query)

        # 4. Set fallback message
        fallback_message = ""
        if intent_type == IntentType.UNKNOWN or (intent_type == IntentType.GENERAL_CHAT and confidence < 0.6):
            fallback_message = self._get_fallback_message()

        result = IntentResult(
            intent_type=intent_type,
            confidence=confidence,
            entities=entities,
            parameters=parameters,
            raw_query=query,
            fallback_message=fallback_message
        )

        logger.info(f"   Intent: {intent_type.value}, Confidence: {confidence:.2f}")
        logger.info(f"   Entities: {len(entities)} items")
        if fallback_message:
            logger.info(f"   Fallback message: Set")

        return result

    def _get_fallback_message(self) -> str:
        """
        Get fallback message
        
        Returns:
            Fallback message text
        """
        return (
            "Hello! Thank you for your question 😊\n\n"
            "Let me introduce the services I can provide:\n\n"
            "**📊 Company In-depth Analysis**\n"
            "   Say: \"Analyze [company name]\" or \"How is [stock ticker]\"\n"
            "   Example: \"Analyze Apple Inc.\" / \"How is AAPL performing\"\n\n"
            "**🏭 Industry Research**\n"
            "   Say: \"[Industry name] industry analysis\"\n"
            "   Example: \"How is the technology industry outlook\" / \"Finance industry analysis\"\n\n"
            "**📰 News Retrieval**\n"
            "   Say: \"Latest news about [company name]\"\n"
            "   Example: \"Recent news about Tesla\" / \"BABA today's updates\"\n\n"
            "Currently supported industries include:\n"
            "Technology, Finance, Healthcare, Consumer Retail, Energy, Automotive Manufacturing, Real Estate, Telecommunications, etc.\n\n"
            "What information would you like to know? 😊"
        )

    def _classify_intent(self, query: str) -> Tuple[IntentType, float]:
        """
        Classify intent type

        Returns:
            (Intent type, Confidence level)
        """
        query_lower = query.lower()
        scores = {}

        # Calculate score for each intent
        for intent_type, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    # Adjust weight based on keyword position
                    score += 1.0

            if score > 0:
                scores[intent_type] = score

        if not scores:
            # If no keywords match, check if there are stock tickers
            tickers = self._extract_tickers(query)
            if tickers:
                # Has stock ticker but no clear intent, default to news query
                return IntentType.NEWS_QUERY, 0.6
            return IntentType.GENERAL_CHAT, 0.5

        # Select the intent with highest score
        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]

        # Calculate confidence (normalized to 0-1)
        total_score = sum(scores.values())
        confidence = min(max_score / total_score, 1.0) if total_score > 0 else 0.5

        # If only one intent matches, increase confidence
        if len(scores) == 1:
            confidence = max(confidence, 0.8)

        return best_intent, confidence

    def _extract_entities(self, query: str) -> List[ExtractedEntity]:
        """Extract entities (companies, stock tickers, time, industries, etc.)"""
        entities = []

        # 1. Extract stock tickers
        tickers = self._extract_tickers(query)
        for ticker in tickers:
            entities.append(ExtractedEntity(
                entity_type='ticker',
                value=ticker,
                confidence=0.9
            ))

        # 2. Extract company names
        companies = self._extract_companies(query)
        for company in companies:
            entities.append(ExtractedEntity(
                entity_type='company',
                value=company,
                confidence=0.85
            ))

            # If corresponding stock ticker exists, add it too
            ticker = self.company_ticker_map.get(company.lower())
            if ticker and ticker not in tickers:
                entities.append(ExtractedEntity(
                    entity_type='ticker',
                    value=ticker,
                    confidence=0.95
                ))

        # 3. Extract industry names
        industries = self._extract_industries(query)
        for industry in industries:
            entities.append(ExtractedEntity(
                entity_type='industry',
                value=industry,
                confidence=0.85
            ))

        # 4. Extract time expressions
        time_expr = self._extract_time_expression(query)
        if time_expr:
            entities.append(ExtractedEntity(
                entity_type='time',
                value=time_expr,
                confidence=0.8
            ))

        return entities

    def _extract_tickers(self, query: str) -> List[str]:
        """Extract stock tickers"""
        # Find uppercase letter combinations (1-5 characters)
        matches = self.ticker_pattern.findall(query)

        # Filter out common non-ticker words
        non_tickers = {'THE', 'AND', 'FOR', 'NOT', 'BUT', 'THIS', 'THAT', 'WITH'}
        tickers = [m for m in matches if m not in non_tickers]

        return tickers

    def _extract_companies(self, query: str) -> List[str]:
        """Extract company names"""
        companies = []
        query_lower = query.lower()

        # Check if contains known company names
        for company_name in self.company_ticker_map.keys():
            if company_name.lower() in query_lower:
                # Use standard name
                standard_name = company_name.title()
                if standard_name not in companies:
                    companies.append(standard_name)

        return companies

    def _extract_industries(self, query: str) -> List[str]:
        """Extract industry names"""
        industries = []
        query_lower = query.lower()

        # Check if contains known industry names
        for industry_name, industry_code in self.industry_map.items():
            if industry_name.lower() in query_lower:
                # Use standard code
                if industry_code not in industries:
                    industries.append(industry_code)

        return industries

    def _extract_time_expression(self, query: str) -> Optional[str]:
        """Extract time expressions"""
        # Check various time patterns
        for time_type, pattern in self.time_patterns.items():
            match = pattern.search(query)
            if match:
                if time_type in ['recent_days', 'recent_weeks', 'recent_months']:
                    # Return standardized time expression
                    num = match.group(1)
                    unit = match.group(2)
                    return f"{num}{unit}"
                else:
                    # Return time type
                    return time_type

        return None

    def _extract_parameters(self, query: str) -> Dict[str, any]:
        """Extract additional parameters"""
        params = {}
        query_lower = query.lower()

        # Detect if detailed analysis is needed
        if any(word in query_lower for word in ['detailed', 'in-depth', 'deep']):
            params['detail_level'] = 'high'
        elif any(word in query_lower for word in ['simple', 'brief']):
            params['detail_level'] = 'low'
        else:
            params['detail_level'] = 'medium'

        # Detect language preference
        if any(word in query_lower for word in ['english', 'en']):
            params['language'] = 'en'
        else:
            params['language'] = 'zh'

        return params


# Convenience function
def recognize_intent(query: str) -> IntentResult:
    """
    Quick intent recognition

    Args:
        query: User query

    Returns:
        Intent recognition result
    """
    recognizer = IntentRecognizer()
    return recognizer.recognize(query)