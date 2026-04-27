"""
Intent Processor - Execute corresponding actions based on recognized intent
"""
import sys
import os
import logging
import importlib
from typing import Dict, Any, Optional

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules
_intent_module = importlib.import_module('06_intent.intent_recognizer')
IntentRecognizer = _intent_module.IntentRecognizer
IntentResult = _intent_module.IntentResult
IntentType = _intent_module.IntentType

_memory_module = importlib.import_module('07_memory.memory_manager')
MemoryManager = _memory_module.MemoryManager

logger = logging.getLogger(__name__)


class IntentProcessor:
    """
    Intent Processor
    - Receive Intent recognition results
    - Route to corresponding processing modules
    - Return processing results
    """

    def __init__(self, memory_manager: MemoryManager = None):
        """
        Initialize intent processor

        Args:
            memory_manager: Memory manager instance
        """
        self.recognizer = IntentRecognizer()
        self.memory = memory_manager or MemoryManager()

        logger.info("✅ Intent processor initialized successfully")

    def process(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process user query

        Args:
            query: User query text
            session_id: Session ID

        Returns:
            Processing result
        """
        # 1. Recognize intent
        intent = self.recognizer.recognize(query)

        # 2. Save to short-term memory (conversation history)
        if session_id:
            self.memory.remember(
                content=f"User query: {query}",
                category=self._intent_to_memory_category(intent.intent_type),
                importance=0.3,
                tags=[intent.intent_type.value]
            )

        # 3. Route based on intent type
        result = self._route_intent(intent, session_id)

        # 4. Add intent information to result
        result['06_intent'] = intent.to_dict()

        return result

    def _route_intent(self, intent: IntentResult, session_id: str = None) -> Dict[str, Any]:
        """
        Route to corresponding handler based on intent type

        Args:
            intent: Intent recognition result
            session_id: Session ID

        Returns:
            Processing result
        """
        handlers = {
            IntentType.COMPANY_ANALYSIS: self._handle_company_analysis,
            IntentType.NEWS_QUERY: self._handle_news_query,
            IntentType.STOCK_COMPARISON: self._handle_stock_comparison,
            IntentType.MARKET_TREND: self._handle_market_trend,
            IntentType.SENTIMENT_ANALYSIS: self._handle_sentiment_analysis,
            IntentType.WATCHLIST_MANAGE: self._handle_watchlist_manage,
            IntentType.MEMORY_QUERY: self._handle_memory_query,
            IntentType.REPORT_GENERATE: self._handle_report_generate,
            IntentType.GENERAL_CHAT: self._handle_general_chat,
        }

        handler = handlers.get(intent.intent_type, self._handle_unknown)

        try:
            return handler(intent, session_id)
        except Exception as e:
            logger.error(f"❌ Intent processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Sorry, an error occurred while processing your request"
            }

    def _handle_company_analysis(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle company analysis intent"""
        tickers = intent.get_tickers()
        companies = intent.get_companies()

        if not tickers and not companies:
            return {
                "success": False,
                "message": "Please specify the company name or stock ticker to analyze",
                "suggestion": "For example: 'Analyze Apple Inc.' or 'Analyze AAPL'"
            }

        # TODO: Call actual report generation module
        return {
            "success": True,
            "action": "company_analysis",
            "tickers": tickers,
            "companies": companies,
            "time_range": intent.get_time_range() or "7 days",
            "message": f"Analyzing {', '.join(companies or tickers)}..."
        }

    def _handle_news_query(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle news query intent"""
        tickers = intent.get_tickers()
        companies = intent.get_companies()

        if not tickers and not companies:
            return {
                "success": False,
                "message": "Please specify the company or stock to query news for",
                "suggestion": "For example: 'Recent news about Apple' or 'AAPL today's updates'"
            }

        # TODO: Call actual news retrieval module
        return {
            "success": True,
            "action": "news_query",
            "tickers": tickers,
            "companies": companies,
            "time_range": intent.get_time_range() or "recent",
            "message": f"Querying news for {', '.join(companies or tickers)}..."
        }

    def _handle_stock_comparison(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle stock comparison intent"""
        tickers = intent.get_tickers()
        companies = intent.get_companies()

        if len(tickers) < 2 and len(companies) < 2:
            return {
                "success": False,
                "message": "Please specify at least two stocks or companies to compare",
                "suggestion": "For example: 'Compare Apple and Microsoft' or 'AAPL vs MSFT'"
            }

        # TODO: Call actual comparison analysis module
        return {
            "success": True,
            "action": "stock_comparison",
            "tickers": tickers,
            "companies": companies,
            "message": f"Comparing {', '.join(companies[:2] or tickers[:2])}..."
        }

    def _handle_market_trend(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle market trend intent"""
        return {
            "success": True,
            "action": "market_trend",
            "message": "Analyzing market trends...",
            "note": "This feature is to be implemented"
        }

    def _handle_sentiment_analysis(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle sentiment analysis intent"""
        tickers = intent.get_tickers()
        companies = intent.get_companies()

        if not tickers and not companies:
            return {
                "success": False,
                "message": "Please specify the company or stock to analyze sentiment for",
                "suggestion": "For example: 'Analyze market sentiment for Apple'"
            }

        # TODO: Call actual sentiment analysis module
        return {
            "success": True,
            "action": "sentiment_analysis",
            "tickers": tickers,
            "companies": companies,
            "message": f"Analyzing market sentiment for {', '.join(companies or tickers)}..."
        }

    def _handle_watchlist_manage(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle watchlist management intent"""
        query_lower = intent.raw_query.lower()
        tickers = intent.get_tickers()
        companies = intent.get_companies()

        # Determine whether to add or remove
        if any(word in query_lower for word in ['add', 'watch']):
            action = "add"
            if tickers or companies:
                ticker = tickers[0] if tickers else self._get_ticker_for_company(companies[0])
                company = companies[0] if companies else ""

                # TODO: Call actual add method
                self.memory.add_to_watchlist(ticker, company)

                return {
                    "success": True,
                    "action": "watchlist_add",
                    "ticker": ticker,
                    "company": company,
                    "message": f"Added {company or ticker} to watchlist"
                }

        elif any(word in query_lower for word in ['remove', 'unwatch']):
            action = "remove"
            # TODO: Implement removal logic
            return {
                "success": True,
                "action": "watchlist_remove",
                "message": "Removal feature to be implemented"
            }

        else:
            # View watchlist
            watchlist = self.memory.get_watchlist()
            return {
                "success": True,
                "action": "watchlist_view",
                "watchlist": watchlist,
                "message": f"Current watchlist: {', '.join(watchlist) if watchlist else 'Empty'}"
            }

        return {
            "success": False,
            "message": "Unrecognized operation, please specify whether to add or remove"
        }

    def _handle_memory_query(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle memory query intent"""
        query = intent.raw_query

        # Retrieve relevant information from long-term memory
        memories = self.memory.recall(query, limit=5)

        if memories:
            context = self.memory.get_context(query, limit=5)
            return {
                "success": True,
                "action": "memory_recall",
                "memories": [m.to_dict() for m in memories],
                "context": context,
                "message": f"Found {len(memories)} related memories"
            }
        else:
            return {
                "success": True,
                "action": "memory_recall",
                "memories": [],
                "message": "No relevant historical memories found"
            }

    def _handle_report_generate(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle report generation intent"""
        tickers = intent.get_tickers()
        companies = intent.get_companies()

        if not tickers and not companies:
            return {
                "success": False,
                "message": "Please specify the company to generate report for",
                "suggestion": "For example: 'Generate analysis report for Apple'"
            }

        # TODO: Call actual report generation module
        return {
            "success": True,
            "action": "report_generate",
            "tickers": tickers,
            "companies": companies,
            "message": f"Generating analysis report for {', '.join(companies or tickers)}..."
        }

    def _handle_general_chat(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle general chat intent"""
        return {
            "success": True,
            "action": "general_chat",
            "message": "Hello! I am a financial analysis assistant, specializing in in-depth company and industry analysis 💼\n\n"
                      "I can help you with:\n"
                      "📊 **Company Analysis**: Fundamentals, financial performance, risk assessment (supports A-shares/HK-shares/US stocks)\n"
                      "🏭 **Industry Research**: Industry trends, competitive landscape, supply chain analysis\n"
                      "📰 **News Retrieval**: Query latest news for specific companies\n"
                      "📈 **Stock Comparison**: Multi-dimensional comparison of different stocks\n"
                      "💼 **Watchlist Management**: Manage your favorite stock list\n\n"
                      "**Usage Examples:**\n"
                      "   • \"Analyze Apple Inc.\"\n"
                      "   • \"Analyze technology industry\"\n"
                      "   • \"Query latest news about AAPL\"\n"
                      "   • \"Compare Apple and Microsoft\"\n\n"
                      "How can I help you? 😊"
        }

    def _handle_unknown(self, intent: IntentResult, session_id: str = None) -> Dict:
        """Handle unknown intent"""
        return {
            "success": False,
            "action": "unknown",
            "message": "Hello! It seems your question is beyond my capabilities 🤔\n\n"
                      "Let me introduce what I can do:\n\n"
                      "**If you want to analyze a company**\n"
                      "   Say: \"Analyze [company name]\" or \"How is [stock ticker]\"\n"
                      "   Example: \"Analyze Apple Inc.\" / \"How is AAPL performing\"\n\n"
                      "**If you want to understand an industry**\n"
                      "   Say: \"[Industry name] industry analysis\"\n"
                      "   Example: \"How is the technology industry outlook\" / \"Finance industry analysis\"\n\n"
                      "**If you want to see latest news**\n"
                      "   Say: \"Latest news about [company name]\"\n"
                      "   Example: \"Recent news about Tesla\" / \"BABA today's updates\"\n\n"
                      "Currently supported industries include:\n"
                      "Technology, Finance, Healthcare, Consumer Retail, Energy, Automotive Manufacturing, Real Estate, Telecommunications, etc.\n\n"
                      "What would you like to know? 😊",
            "suggestion": "Please use clearer expressions, such as 'Analyze Apple Inc.' or 'Query news about AAPL'"
        }

    def _intent_to_memory_category(self, intent_type: IntentType):
        """Convert intent type to memory category"""
        _memory_types_module = importlib.import_module('07_memory.memory_types')
        MemoryCategory = _memory_types_module.MemoryCategory

        mapping = {
            IntentType.COMPANY_ANALYSIS: MemoryCategory.COMPANY_ANALYSIS,
            IntentType.NEWS_QUERY: MemoryCategory.CONVERSATION,
            IntentType.STOCK_COMPARISON: MemoryCategory.CONVERSATION,
            IntentType.WATCHLIST_MANAGE: MemoryCategory.WATCHLIST,
            IntentType.MEMORY_QUERY: MemoryCategory.CONVERSATION,
        }

        return mapping.get(intent_type, MemoryCategory.CONVERSATION)

    def _get_ticker_for_company(self, company_name: str) -> str:
        """Get stock ticker based on company name"""
        company_lower = company_name.lower()

        # Look up from recognizer's mapping table
        for name, ticker in self.recognizer.company_ticker_map.items():
            if name in company_lower or company_lower in name:
                return ticker

        # If not found, return uppercase company name
        return company_name.upper().replace(" ", "_")[:5]