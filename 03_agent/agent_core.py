"""
Financial Analysis Agent Core
Integrates intent recognition, memory, RAG, and report generation
Supports multi-turn conversation and context understanding
Automatically decides whether to use cloud or local models
"""
import sys
import os
import uuid
import logging
import importlib
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Agent State"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"


class AgentMode(str, Enum):
    """Agent Mode"""
    CHAT = "chat"
    ANALYSIS = "analysis"
    REPORT = "report"


class FinancialAgent:
    """
    Financial Analysis Agent
    - Integrates intent recognition, memory, RAG, and report generation
    - Supports multi-turn conversation and context understanding
    - Automatically decides whether to use cloud or local models
    """

    def __init__(self, 
                 user_id: str = "default",
                 use_cloud_llm: bool = None,
                 device: str = None,
                 verbose: bool = False):
        """
        Initialize Agent
        
        Args:
            user_id: User ID
            use_cloud_llm: Whether to use cloud LLM (None=auto detect)
            device: Computing device
            verbose: Whether to show detailed logs
        """
        self.user_id = user_id
        self.agent_id = str(uuid.uuid4())[:8]
        self.state = AgentState.IDLE
        self.mode = AgentMode.CHAT
        self.verbose = verbose
        
        # Initialize session
        self.session_id = None
        
        if verbose:
            logger.info(f"🤖 Initializing Agent: {self.agent_id}")
            logger.info(f"   User: {user_id}")
        
        # Lazy initialize components (avoid circular imports)
        self._initialized = False
        self.use_cloud_llm = use_cloud_llm
        self.device = device

    def initialize(self):
        """Initialize all components"""
        if self._initialized:
            return
        
        if self.verbose:
            logger.info("🔧 Initializing Agent components...")
        
        # 1. Initialize memory system
        _memory_module = importlib.import_module('07_memory.memory_manager')
        MemoryManager = _memory_module.MemoryManager
        self.memory = MemoryManager(user_id=self.user_id)
        
        # 2. Initialize intent recognition
        _intent_module = importlib.import_module('06_intent.intent_processor')
        IntentProcessor = _intent_module.IntentProcessor
        self.intent_processor = IntentProcessor(memory_manager=self.memory)
        
        # 3. Initialize RAG service
        _retrieve_module = importlib.import_module('09_retrieve.rag_service')
        RAGService = _retrieve_module.RAGService
        self.rag = RAGService(device=self.device)
        
        # 4. Initialize LLM
        model_name = self._get_default_model()
        if self.verbose:
            logger.info(f"📥 Loading LLM: {model_name}")
        self.rag.initialize_llm(model=model_name, use_cloud=self.use_cloud_llm)
        
        self._initialized = True
        if self.verbose:
            logger.info("✅ Agent component initialization complete")

    def start_session(self, session_id: str = None) -> str:
        """Start new session"""
        if not self._initialized:
            self.initialize()
        
        self.session_id = self.memory.start_session(session_id)
        self.state = AgentState.IDLE
        
        if self.verbose:
            logger.info(f"🚀 Starting session: {self.session_id[:8]}...")
        return self.session_id

    def chat(self, message: str, **kwargs) -> Dict[str, Any]:
        """Chat with Agent (main interface)"""
        if not self._initialized:
            self.initialize()
        
        if not self.session_id:
            self.start_session()
        
        self.state = AgentState.THINKING
        
        try:
            # 1. Intent recognition
            intent_result = self.intent_processor.recognizer.recognize(message)
            
            # 2. Retrieve related memories
            context_memories = self.memory.recall(message, limit=3)
            context_text = self._format_context(context_memories)
            
            # 3. Process based on intent type
            response = self._handle_intent(intent_result, context_text, **kwargs)
            
            # 4. Save to memory
            self._save_interaction(message, response, intent_result)
            
            self.state = AgentState.COMPLETED
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "response": response,
                "intent": intent_result.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"❌ Agent processing failed: {e}")
            
            return {
                "success": False,
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "error": str(e),
                "response": {
                    "message": "Sorry, an error occurred while processing your request",
                    "type": "error"
                },
                "timestamp": datetime.now().isoformat()
            }

    def analyze_company(self, ticker: str, company_name: str = None, 
                       days: int = 7, **kwargs) -> Dict[str, Any]:
        """Analyze company (dedicated interface)"""
        if not self._initialized:
            self.initialize()
        
        if not company_name:
            company_name = ticker
        
        self.state = AgentState.EXECUTING

        try:
            _report_module = importlib.import_module('11_report.report_generator')
            analyze_company_and_generate_report = _report_module.analyze_company_and_generate_report

            result = analyze_company_and_generate_report(
                company_name=company_name,
                ticker=ticker,
                days=days,
                use_cloud=self.use_cloud_llm,
                device=self.device,
                output_dir="output"
            )

            if result.get('success'):
                summary = result.get('summary', '')[:200]
                self.memory.save_analysis_result(
                    ticker=ticker,
                    company_name=company_name,
                    analysis_summary=summary,
                    report_path=result.get('report_path', '')
                )

            self.state = AgentState.COMPLETED

            return {
                "success": True,
                "action": "company_analysis",
                "ticker": ticker,
                "company_name": company_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"❌ Company analysis failed: {e}")

            return {
                "success": False,
                "action": "company_analysis",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def analyze_industry(self, industry: str, industry_name: str = None, 
                        days: int = 7, **kwargs) -> Dict[str, Any]:
        """Analyze industry (dedicated interface)"""
        if not self._initialized:
            self.initialize()
        
        if not industry_name:
            industry_name = industry
        
        self.state = AgentState.EXECUTING

        try:
            _report_module = importlib.import_module('11_report.report_generator')
            generate_industry_report = _report_module.generate_industry_report

            result = generate_industry_report(
                industry=industry,
                industry_name=industry_name,
                days=days,
                use_cloud=self.use_cloud_llm,
                device=self.device,
                output_dir="output"
            )

            self.state = AgentState.COMPLETED

            return {
                "success": True,
                "action": "industry_analysis",
                "industry": industry,
                "industry_name": industry_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"❌ Industry analysis failed: {e}")

            return {
                "success": False,
                "action": "industry_analysis",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def query_news(self, ticker: str, days: int = 7, limit: int = 10) -> Dict[str, Any]:
        """Query news"""
        if not self._initialized:
            self.initialize()
        
        self.state = AgentState.EXECUTING
        
        try:
            # Query news for specific ticker directly from Milvus
            from datetime import datetime, timedelta
            
            now = datetime.now()
            start_time = now - timedelta(days=days)
            start_timestamp = int(start_time.timestamp())
            
            # Access Milvus using RAGSearcher's retriever
            all_news = self.rag.searcher.retriever.vector_db.client.query(
                collection_name=self.rag.searcher.retriever.vector_db.collection_name,
                filter=f"ticker == '{ticker}' && publish_time >= {start_timestamp}",
                limit=limit,
                output_fields=[
                    "id", "ticker", "headline", "summary", "url", "source",
                    "publish_time", "event_type", "industry", 
                    "sentiment_polarity", "sentiment_intensity"
                ]
            )
            
            # Sort by time (newest first)
            all_news.sort(key=lambda x: x.get('publish_time', 0), reverse=True)

            self.state = AgentState.COMPLETED

            return {
                "success": True,
                "action": "news_query",
                "ticker": ticker,
                "count": len(all_news),
                "news": all_news,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"❌ News query failed: {e}")

            return {
                "success": False,
                "action": "news_query",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def end_session(self) -> bool:
        """End current session"""
        if self.session_id:
            result = self.memory.end_session()
            self.session_id = None
            self.state = AgentState.IDLE
            return result
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get Agent status"""
        return {
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "state": self.state.value,
            "mode": self.mode.value,
            "session_id": self.session_id,
            "initialized": self._initialized
        }

    def close(self):
        """Close Agent and release resources"""
        if self._initialized:
            self.memory.close()
            self._initialized = False

    # ========== Private Methods ==========

    def _handle_intent(self, intent_result, context_text: str, **kwargs) -> Dict:
        """Handle recognized intent"""
        _intent_module = importlib.import_module('06_intent.intent_recognizer')
        IntentType = _intent_module.IntentType

        intent_type = intent_result.intent_type

        if intent_type == IntentType.COMPANY_ANALYSIS:
            return self._process_company_analysis(intent_result, context_text)
        elif intent_type == IntentType.INDUSTRY_ANALYSIS:
            return self._process_industry_analysis(intent_result, context_text)
        elif intent_type == IntentType.NEWS_QUERY:
            return self._process_news_query(intent_result, context_text)
        elif intent_type == IntentType.MEMORY_QUERY:
            return self._process_memory_query(intent_result, context_text)
        elif intent_type == IntentType.PREFERENCE_QUERY:
            return self._process_preference_query(intent_result, context_text)
        elif intent_type == IntentType.WATCHLIST_MANAGE:
            return self._process_watchlist(intent_result, context_text)
        elif intent_type == IntentType.GENERAL_CHAT:
            return self._process_general_chat(intent_result, context_text)
        elif intent_type == IntentType.UNKNOWN:
            return self._process_unknown_intent(intent_result, context_text)
        else:
            return self._generate_llm_response(intent_result, context_text)

    def _process_general_chat(self, intent_result, context_text: str) -> Dict:
        """Handle general chat intent"""
        # If there's a fallback message (low confidence), prioritize it
        if intent_result.fallback_message:
            return {
                "message": intent_result.fallback_message,
                "type": "clarification"
            }
        
        # Otherwise use LLM to generate friendly chat response
        return self._generate_llm_response(intent_result, context_text)

    def _process_unknown_intent(self, intent_result, context_text: str) -> Dict:
        """Handle unknown intent"""
        # If there's a fallback message, prioritize it
        if intent_result.fallback_message:
            return {
                "message": intent_result.fallback_message,
                "type": "clarification"
            }
        
        # Otherwise use LLM to generate response
        return self._generate_llm_response(intent_result, context_text)

    def _process_company_analysis(self, intent_result, context_text: str) -> Dict:
        """Handle company analysis intent"""
        # Check if clarification is needed
        if intent_result.fallback_message:
            return {
                "message": intent_result.fallback_message,
                "type": "clarification"
            }

        tickers = intent_result.get_tickers()
        companies = intent_result.get_companies()

        # Prioritize stock ticker extracted by LLM
        ticker = tickers[0] if tickers else None
        company = companies[0] if companies else None
        
        # If only company name without ticker, try to infer
        if not ticker and company:
            ticker = self._infer_ticker(company)
        
        if not ticker and not company:
            return {
                "message": "Please specify the company name or stock ticker to analyze",
                "type": "clarification"
            }

        days = self._parse_time_to_days(intent_result.get_time_range()) or 7

        result = self.analyze_company(ticker, company, days)

        if result.get('success'):
            return {
                "message": f"✅ {company or ticker} analysis complete",
                "type": "analysis_result",
                "data": result
            }
        else:
            return {
                "message": f"❌ Analysis error: {result.get('error')}",
                "type": "error"
            }

    def _process_industry_analysis(self, intent_result, context_text: str) -> Dict:
        """Handle industry analysis intent"""
        # Check if clarification is needed
        if intent_result.fallback_message:
            return {
                "message": intent_result.fallback_message,
                "type": "clarification"
            }

        industries = intent_result.get_industries()

        if not industries:
            return {
                "message": "Please specify the industry to analyze (e.g., Technology, Finance, Healthcare, etc.)",
                "type": "clarification"
            }

        industry = industries[0]
        industry_name = self._get_industry_name(industry)
        days = self._parse_time_to_days(intent_result.get_time_range()) or 7

        result = self.analyze_industry(industry, industry_name, days)

        if result.get('success'):
            return {
                "message": f"✅ {industry_name} industry analysis complete",
                "type": "analysis_result",
                "data": result
            }
        else:
            return {
                "message": f"❌ Analysis error: {result.get('error')}",
                "type": "error"
            }

    def _process_news_query(self, intent_result, context_text: str) -> Dict:
        """Handle news query intent"""
        # Check if clarification is needed
        if intent_result.fallback_message:
            return {
                "message": intent_result.fallback_message,
                "type": "clarification"
            }

        tickers = intent_result.get_tickers()
        companies = intent_result.get_companies()
        
        if not tickers and not companies:
            return {"message": "Please specify the company to query news for", "type": "clarification"}
        
        # Prioritize stock ticker extracted by LLM
        ticker = tickers[0] if tickers else None
        if not ticker and companies:
            ticker = self._infer_ticker(companies[0])
        
        days = self._parse_time_to_days(intent_result.get_time_range()) or 7
        
        # Set a large limit to get all matching news
        result = self.query_news(ticker, days=days, limit=1000)
        
        if result.get('success'):
            return {
                "message": f"Found {result.get('count')} news items",
                "type": "news_list",
                "data": result
            }
        else:
            return {"message": f"Error querying news", "type": "error"}

    def _process_memory_query(self, intent_result, context_text: str) -> Dict:
        """Handle memory query intent"""
        memories = self.memory.recall(intent_result.raw_query, limit=5)
        
        if memories:
            return {
                "message": f"Found {len(memories)} related memories",
                "type": "memory_recall"
            }
        else:
            return {"message": "No relevant historical memories found", "type": "info"}

    def _process_preference_query(self, intent_result, context_text: str) -> Dict:
        """Handle investment preference query intent"""
        preferences = self.get_investment_preferences()
        
        summary = preferences.get('summary', {})
        companies = summary.get('companies', [])
        industries = summary.get('industries', [])
        
        if not companies and not industries:
            return {
                "message": "You haven't set investment preferences yet. I'll automatically record your preferences when you analyze companies or industries.",
                "type": "preference_info"
            }
        
        message_parts = ["📊 Your Investment Preferences:"]
        
        if companies:
            message_parts.append(f"\n🏢 Preferred Companies ({len(companies)}):")
            for company in companies[:10]:
                message_parts.append(f"  • {company}")
            if len(companies) > 10:
                message_parts.append(f"  ... {len(companies) - 10} more")
        
        if industries:
            message_parts.append(f"\n🏭 Preferred Industries ({len(industries)}):")
            for industry in industries:
                message_parts.append(f"  • {industry}")
        
        return {
            "message": "\n".join(message_parts),
            "type": "preference_list",
            "data": preferences
        }

    def get_investment_preferences(self) -> Dict[str, Any]:
        """Get user investment preferences"""
        if not self._initialized:
            self.initialize()
        
        preferences = self.memory.get_investment_preferences()
        
        return {
            "success": True,
            "preferences": preferences,
            "summary": {
                "total_companies": len(preferences["tickers"]),
                "total_industries": len(preferences["industries"]),
                "companies": list(preferences["companies"]),
                "tickers": list(preferences["tickers"]),
                "industries": list(preferences["industries"])
            }
        }

    def _process_watchlist(self, intent_result, context_text: str) -> Dict:
        """Handle watchlist intent"""
        query_lower = intent_result.raw_query.lower()
        
        if any(word in query_lower for word in ['view', 'list']):
            watchlist = self.memory.get_watchlist()
            return {
                "message": f"Current watchlist: {', '.join(watchlist) if watchlist else 'Empty'}",
                "type": "watchlist_view",
                "watchlist": watchlist
            }
        
        return {"message": "Please specify the operation type", "type": "clarification"}

    def _generate_llm_response(self, intent_result, context_text: str) -> Dict:
        """Generate general response using LLM"""
        # If there's a fallback message and confidence is low, prioritize fallback
        if intent_result.fallback_message and intent_result.confidence <= 0.6:
            return {
                "message": intent_result.fallback_message,
                "type": "clarification"
            }
        
        try:
            system_message = "You are a professional financial analysis assistant."
            user_message = intent_result.raw_query
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            content = self.rag.llm_client.chat(
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                "message": content,
                "type": "llm_response"
            }
        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
            return {
                "message": "Sorry, I cannot answer this question at the moment",
                "type": "error"
            }

    def _format_context(self, memories) -> str:
        """Format memories into context string"""
        if not memories:
            return ""
        
        lines = ["Related Historical Memories:"]
        for i, memory in enumerate(memories, 1):
            lines.append(f"{i}. {memory.content[:150]}")
        
        return "\n".join(lines)

    def _save_interaction(self, user_message: str, response: Dict, intent_result):
        """Save interaction to memory"""
        _memory_module = importlib.import_module('07_memory.memory_types')
        MemoryCategory = _memory_module.MemoryCategory
        
        self.memory.remember(
            content=f"User: {user_message}",
            category=MemoryCategory.CONVERSATION,
            importance=0.3,
            tags=[intent_result.intent_type.value]
        )

    def _get_default_model(self) -> str:
        """Get default model"""
        _config_module = importlib.import_module('05_config.settings')
        Config = _config_module.Config
        
        if self.use_cloud_llm is None:
            return Config.DEFAULT_LLM_MODEL
        elif self.use_cloud_llm:
            return Config.QWEN_CLOUD_MODEL
        else:
            return Config.HF_MODEL_NAME

    def _infer_ticker(self, company_name: str) -> str:
        """Infer stock ticker from company name"""
        _intent_module = importlib.import_module('06_intent.intent_recognizer')
        IntentRecognizer = _intent_module.IntentRecognizer
        recognizer = IntentRecognizer()
        
        for name, ticker in recognizer.company_ticker_map.items():
            if name in company_name.lower():
                return ticker
        
        return company_name.upper().replace(" ", "_")[:5]

    def _get_industry_name(self, industry_code: str) -> str:
        """Get industry name from industry code"""
        industry_names = {
            'technology': 'Technology Industry',
            'finance': 'Finance Industry',
            'healthcare_pharma': 'Healthcare & Pharmaceuticals',
            'consumer_retail': 'Consumer Retail',
            'energy_utilities': 'Energy & Utilities',
            'automotive_manufacturing': 'Automotive & Manufacturing',
            'real_estate': 'Real Estate',
            'telecommunications': 'Telecommunications'
        }
        return industry_names.get(industry_code, industry_code)

    def _parse_time_to_days(self, time_expr: Optional[str]) -> Optional[int]:
        """Convert time expression to days"""
        if not time_expr:
            return None
        
        import re
        match = re.match(r'(\d+)(days?|weeks?|months?)', time_expr)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            
            if unit.startswith('day'):
                return num
            elif unit.startswith('week'):
                return num * 7
            elif unit.startswith('month'):
                return num * 30
        
        return 7

