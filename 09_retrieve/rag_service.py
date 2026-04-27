"""
RAG Service Interface - Unified RAG retrieval and analysis service
Provides simple and easy-to-use interfaces for external calls
"""
import sys
import os
import logging
import importlib
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules starting with numbers
retrieve_module = importlib.import_module('09_retrieve.rag_searcher')
RAGSearcher = retrieve_module.RAGSearcher
ImpactAnalyzer = retrieve_module.ImpactAnalyzer

llm_module = importlib.import_module('09_retrieve.llm_client')
UnifiedLLMClient = llm_module.UnifiedLLMClient
create_llm_client = llm_module.create_llm_client

evaluation_module = importlib.import_module('09_retrieve.evaluation')
AnalysisEvaluator = evaluation_module.AnalysisEvaluator

config_module = importlib.import_module('05_config.settings')
Config = config_module.Config

# Import Prompt loader
from .prompt_loader import get_prompt_loader

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG Service Interface

    Usage Example:
        # Initialize service
        rag_service = RAGService(device='cuda')
        rag_service.initialize_bm25(limit=500)

        # Simple search
        results = rag_service.search(query="Apple earnings", limit=10)

        # Advanced search
        results = rag_service.advanced_search(
            query="AI technology",
            event_type="product_launch",
            industry="technology",
            vector_weight=0.7,
            bm25_weight=0.3
        )

        # Complete flow: retrieval + build Impact Analysis Prompt
        analysis_data = rag_service.retrieve_and_analyze(current_news)
    """

    def __init__(self, device: str = None, llm_model: str = None):
        """
        Initialize RAG service

        Args:
            device: Computing device ('cuda' or 'cpu')
            llm_model: LLM model name, if not specified use DEFAULT_LLM_MODEL from .env
        """
        self.searcher = RAGSearcher(device=device)
        self.analyzer = ImpactAnalyzer()
        self._bm25_initialized = False

        # Initialize Prompt loader
        self.prompt_loader = get_prompt_loader()

        # Initialize LLM client (if specified or configured in .env)
        self.llm_client = None
        model_to_use = llm_model or Config.DEFAULT_LLM_MODEL

        if model_to_use:
            try:
                self.llm_client = create_llm_client(model=model_to_use, device=device)
                logger.info(f"✅ LLM client initialized: {model_to_use}")
            except Exception as e:
                logger.warning(f"⚠️  LLM client initialization failed: {e}")

        logger.info("✅ RAG service initialized successfully")

    def initialize_llm(self, model: str = None, host: str = None, use_cloud: bool = None):
        """
        Initialize LLM client

        Args:
            model: Model name (if not specified, use configuration from .env)
            host: Reserved parameter (compatible with old interface, not actually used)
            use_cloud: Whether to force cloud usage (True=cloud, False=local, None=auto detect)
        """
        try:
            model_to_use = model or Config.DEFAULT_LLM_MODEL

            self.llm_client = create_llm_client(
                model=model_to_use,
                use_cloud=use_cloud
            )

            if self.llm_client.check_model_availability():
                logger.info(f"✅ LLM model '{model_to_use}' ready")
            else:
                logger.warning(f"⚠️  Model '{model_to_use}' not available")
        except Exception as e:
            logger.error(f"❌ LLM initialization failed: {e}")
            raise

    def initialize_bm25(self, limit: int = 1000):
        """
        Initialize BM25 retriever

        Args:
            limit: Maximum document count
        """
        if not self._bm25_initialized:
            self.searcher.initialize_bm25(limit=limit)
            self._bm25_initialized = True
            logger.info(f"✅ BM25 retriever initialized, max documents: {limit}")
        else:
            logger.info("⚠️  BM25 retriever already initialized, no need to reinitialize")

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Simple search

        Args:
            query: Query text
            limit: Number of results to return

        Returns:
            Search result list
        """
        return self.searcher.search(query=query, limit=limit)

    def advanced_search(self,
                        query: str,
                        event_type: Optional[str] = None,
                        industry: Optional[str] = None,
                        vector_weight: float = 0.7,
                        bm25_weight: float = 0.3,
                        limit: int = 10) -> List[Dict]:
        """
        Advanced search

        Args:
            query: Query text
            event_type: Event type
            industry: Industry
            vector_weight: Vector weight
            bm25_weight: BM25 weight
            limit: Number of results to return

        Returns:
            Search result list
        """
        if self._bm25_initialized:
            # Use hybrid retrieval
            return self.searcher.retriever.hybrid_retrieval(
                query=query,
                event_type=event_type or "",
                industry=industry or "",
                vector_top_k=limit * 2,
                bm25_top_k=limit * 2,
                final_top_k=limit,
                vector_weight=vector_weight,
                bm25_weight=bm25_weight
            )
        else:
            # Use only vector retrieval
            return self.searcher.semantic_search(
                query=query,
                event_type=event_type or "",
                industry=industry or "",
                limit=limit
            )

    def retrieve_and_analyze(self,
                            current_news: Dict,
                            query: str = "",
                            context_limit: int = 10,
                            vector_weight: float = 0.7,
                            bm25_weight: float = 0.3) -> Dict:
        """
        Complete flow: RAG retrieval + build Impact Analysis Prompt

        Args:
            current_news: Current news to analyze
            query: Query text (optional, default uses news content)
            context_limit: Context count
            vector_weight: Vector weight
            bm25_weight: BM25 weight

        Returns:
            Complete result containing retrieval results and Impact Analysis Prompt
        """
        logger.info("\n" + "="*70)
        logger.info("🚀 Starting complete flow (RAG + Build Impact Analysis Prompt)")
        logger.info("="*70)

        # 1. Build query
        if not query:
            query = f"{current_news.get('headline', '')} {current_news.get('summary', '')}"

        logger.info(f"\n🔍 Query: {query[:100]}...")

        # 2. RAG retrieval
        logger.info("\n📊 Executing RAG retrieval...")
        results = self.advanced_search(
            query=query,
            event_type=current_news.get('event_type', ''),
            industry=current_news.get('industry', ''),
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
            limit=context_limit
        )

        logger.info(f"✅ Retrieved {len(results)} related news items")

        # 3. Extract context
        context = self.extract_context_for_llm(results)

        # 4. Build Impact Analysis Prompt
        logger.info("\n📝 Building Impact Analysis Prompt...")
        prompt = self.analyzer.build_prompt(current_news, context)

        logger.info(f"✅ Prompt building complete ({len(prompt)} characters)")

        # 5. Call LLM
        if self.llm_client:
            logger.info("\n🤖 Calling LLM for analysis...")
            llm_result = self.llm_client.generate_impact_analysis(prompt)

            # Parse LLM response
            logger.info("\n📝 Parsing LLM response...")
            json_convertor_module = importlib.import_module('09_retrieve.json_convertor')
            parse_llm_raw_response = json_convertor_module.parse_llm_raw_response
            parsed_llm = parse_llm_raw_response(llm_result.get('raw_response', ''))

            if parsed_llm:
                logger.info("✅ LLM response parsing successful")
            else:
                logger.warning("⚠️  LLM response parsing failed")
        else:
            logger.warning("⚠️  LLM client not initialized, skipping analysis")
            parsed_llm = {}

        # 6. Merge results
        final_result = {
            'current_news': current_news,
            'retrieved_news': results,
            'context': context,
            'prompt': prompt,
            'llm_analysis': parsed_llm,
            'analysis_complete': bool(parsed_llm)
        }

        logger.info("="*70)
        logger.info("✅ Complete flow execution finished")
        logger.info("="*70)

        return final_result

    def analyze_industry_comprehensive(self, 
                                      industry: str,
                                      industry_name: str = None,
                                      days: int = None,
                                      temperature: float = None) -> Dict:
        """
        Comprehensive industry analysis (based on all news from last N days)
        
        Args:
            industry: Industry code
            industry_name: Industry name
            days: Analysis days (default read from configuration file)
            temperature: LLM temperature parameter
            
        Returns:
            Complete industry analysis report
        """
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        # Use default values from configuration file
        days = days or Config.ANALYSIS_DAYS
        temperature = temperature if temperature is not None else Config.LLM_TEMPERATURE
        
        # Read RAG Top-K configuration from environment variable
        rag_top_k = int(os.getenv("RAG_TOP_K", "30"))
        
        logger.info("\n" + "="*70)
        logger.info(f"🚀 Starting comprehensive industry analysis for {industry_name or industry} (last {days} days)")
        logger.info("="*70)
        logger.info(f"📊 RAG Top-K: {rag_top_k}")
        
        # 1. Calculate time range
        now = datetime.now()
        start_time = now - timedelta(days=days)
        start_timestamp = int(start_time.timestamp())
        
        logger.info(f"\n📅 Time range: {start_time.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
        
        # 2. Get all news for this industry within specified days from Milvus
        logger.info(f"\n📊 Fetching news for {industry} industry from last {days} days from Milvus...")
        try:
            all_news = self.searcher.retriever.vector_db.client.query(
                collection_name=self.searcher.retriever.vector_db.collection_name,
                filter=f"industry == '{industry}' && publish_time >= {start_timestamp}",
                limit=rag_top_k,
                output_fields=[
                    "id", "ticker", "headline", "summary", "url", "source",
                    "publish_time", "event_type", "industry", 
                    "sentiment_polarity", "sentiment_intensity",
                    "primary_impact", "business_impacts"
                ]
            )

            # Sort by time (newest first)
            all_news.sort(key=lambda x: x.get('publish_time', 0), reverse=True)
            
            logger.info(f"✅ Found {len(all_news)} news items for {industry} industry in last {days} days")
        except Exception as e:
            logger.error(f"❌ Failed to query industry news: {e}")
            return {"error": f"Query failed: {str(e)}"}
        
        if not all_news:
            logger.warning(f"⚠️  No news found for {industry} industry in last {days} days")
            return {"error": f"No news found for {industry} industry in last {days} days"}
        
        # 3. Statistics overview
        event_types = {}
        sentiments = {}
        companies_involved = set()
        recent_headlines = []
        
        for news in all_news:
            et = news.get('event_type', 'unknown')
            sp = news.get('sentiment_polarity', 'unknown')
            ticker = news.get('ticker', '')
            
            event_types[et] = event_types.get(et, 0) + 1
            sentiments[sp] = sentiments.get(sp, 0) + 1
            
            if ticker:
                companies_involved.add(ticker)
            
            if len(recent_headlines) < 10:
                recent_headlines.append({
                    'headline': news.get('headline', ''),
                    'time': datetime.fromtimestamp(news.get('publish_time', 0)).strftime('%Y-%m-%d') if news.get('publish_time') else 'Unknown',
                    'sentiment': sp,
                    'ticker': ticker,
                    'url': news.get('url', '')
                })
        
        # 4. Build industry analysis Prompt using YAML template
        logger.info("\n📝 Building industry analysis Prompt...")
        
        # Get template configuration
        template_config = self.prompt_loader.get_config('industry_analysis')
        max_recent = template_config.get('max_recent_headlines', 5)
        max_representative = template_config.get('max_representative_news', 15)
        headline_max_len = template_config.get('headline_max_length', 100)
        summary_max_len = template_config.get('summary_max_length', 200)
        per_type = template_config.get('representative_per_type', 2)
        
        # Build industry information
        industry_info = f"""【Industry Information】
Industry Code: {industry}
Industry Name: {industry_name or industry}
Analysis Time: {now.strftime('%Y-%m-%d %H:%M')}
Analysis Period: Last {days} days ({start_time.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')})
Companies Involved: {', '.join(sorted(companies_involved))}
"""
        
        # Build news overview
        news_overview = f"""
【News Data Overview】
Total News: {len(all_news)} items
Event Type Distribution: {', '.join([f'{k}: {v} items' for k, v in sorted(event_types.items(), key=lambda x: x[1], reverse=True)])}
Sentiment Distribution: {', '.join([f'{k}: {v} items' for k, v in sorted(sentiments.items(), key=lambda x: x[1], reverse=True)])}
"""
        
        # Build recent news section (condensed version)
        recent_headlines_limited = recent_headlines[:max_recent]
        recent_news_text = "\n".join([
            f"- [{h['time']}] {h['headline'][:headline_max_len]}... (Sentiment: {h['sentiment']}, Company: {h['ticker']})"
            for h in recent_headlines_limited
        ])
        
        recent_news_section = f"""
【Last {max_recent} News Headlines】
{recent_news_text}
"""
        
        # Select representative news
        representative_news = []
        selected_ids = set()
        
        by_event_type = {}
        for news in all_news:
            et = news.get('event_type', 'other')
            if et not in by_event_type:
                by_event_type[et] = []
            by_event_type[et].append(news)
        
        for et, news_list in by_event_type.items():
            for news in news_list[:per_type]:
                if news['id'] not in selected_ids:
                    representative_news.append(news)
                    selected_ids.add(news['id'])
        
        # Build representative news text (condensed version)
        representative_text = "\n".join([
            f"""
【News {i+1}】
Headline: {news.get('headline', '')[:headline_max_len]}
Time: {datetime.fromtimestamp(news.get('publish_time', 0)).strftime('%Y-%m-%d') if news.get('publish_time') else 'Unknown'}
Company: {news.get('ticker', '')}
Summary: {news.get('summary', '')[:summary_max_len]}
Event Type: {news.get('event_type', '')}
Sentiment: {news.get('sentiment_polarity', '')}
URL: {news.get('url', '')}
"""
            for i, news in enumerate(representative_news[:max_representative])
        ])
        
        # Render Prompt using YAML template
        prompt = self.prompt_loader.render_template(
            'industry_analysis',
            industry=industry,
            industry_name=industry_name or industry,
            days=days,
            analysis_date=now.strftime('%Y-%m-%d'),
            total_news=len(all_news),
            companies_covered=sorted(list(companies_involved)),
            industry_info=industry_info,
            news_overview=news_overview,
            recent_news_section=recent_news_section,
            representative_text=representative_text
        )
        
        # 5. Call LLM for analysis
        logger.info("\n🤖 Calling LLM for comprehensive industry analysis...")
        llm_result = self.llm_client.generate_impact_analysis(
            prompt=prompt,
            temperature=temperature
        )
        
        # Parse LLM returned raw_response
        logger.info("\n📝 Parsing LLM response...")
        if 'raw_response' in llm_result:
            json_convertor_module = importlib.import_module('09_retrieve.json_convertor')
            parse_llm_raw_response = json_convertor_module.parse_llm_raw_response
            parsed_llm = parse_llm_raw_response(llm_result['raw_response'])
            
            if parsed_llm:
                logger.info("✅ LLM response parsing successful")
                logger.info(f"   Parsed fields: {list(parsed_llm.keys())}")
            else:
                logger.warning("⚠️  LLM response parsing failed, using raw result")
                parsed_llm = llm_result
        else:
            logger.warning("⚠️  No raw_response field in LLM result")
            parsed_llm = llm_result
        
        # 6. Merge results
        final_result = {
            'industry': industry,
            'industry_name': industry_name,
            'analysis_period_days': days,
            'start_date': start_time.strftime('%Y-%m-%d'),
            'end_date': now.strftime('%Y-%m-%d'),
            'total_news': len(all_news),
            'companies_covered': sorted(list(companies_involved)),
            'news_overview': {
                'event_types': event_types,
                'sentiments': sentiments,
                'recent_headlines': recent_headlines
            },
            'llm_analysis': parsed_llm,
            'analysis_complete': True,
            'all_news_urls': [news.get('url') for news in all_news if news.get('url')]
        }
        
        # 7. Automatically evaluate analysis quality
        logger.info("\n📊 Starting quality evaluation...")
        evaluator = AnalysisEvaluator()
        quality_report = evaluator.evaluate_analysis(parsed_llm)
        final_result['quality_evaluation'] = quality_report
        
        logger.info(f"✅ Quality evaluation complete - Total Score: {quality_report['overall_score']:.2f}, Grade: {quality_report['grade']}")
        logger.info("="*70)
        
        return final_result
    
    def analyze_company(self,
                       ticker: str,
                       company_name: str = None,
                       days: int = None,
                       temperature: float = None) -> Dict:
        """
        Comprehensive company analysis (based on all news from last N days)
        
        Args:
            ticker: Stock ticker
            company_name: Company name
            days: Analysis days (default read from configuration file)
            temperature: LLM temperature parameter
            
        Returns:
            Complete company analysis report
        """
        if not self.llm_client:
            raise RuntimeError("LLM client not initialized")
        
        # Use default values from configuration file
        days = days or Config.ANALYSIS_DAYS
        temperature = temperature if temperature is not None else Config.LLM_TEMPERATURE
        
        # Read RAG Top-K configuration from environment variable
        rag_top_k = int(os.getenv("RAG_TOP_K", "30"))
        
        logger.info("\n" + "="*70)
        logger.info(f"🚀 Starting comprehensive company analysis for {company_name or ticker} ({ticker}) (last {days} days)")
        logger.info("="*70)
        logger.info(f"📊 RAG Top-K: {rag_top_k}")
        
        # 1. Calculate time range
        now = datetime.now()
        start_time = now - timedelta(days=days)
        start_timestamp = int(start_time.timestamp())
        
        logger.info(f"\n📅 Time range: {start_time.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
        
        # 2. Get all news for this company within specified days from Milvus
        logger.info(f"\n📊 Fetching news for {ticker} from last {days} days from Milvus...")
        try:
            all_news = self.searcher.retriever.vector_db.client.query(
                collection_name=self.searcher.retriever.vector_db.collection_name,
                filter=f"ticker == '{ticker}' && publish_time >= {start_timestamp}",
                limit=rag_top_k,
                output_fields=[
                    "id", "ticker", "headline", "summary", "url", "source",
                    "publish_time", "event_type", "industry", 
                    "sentiment_polarity", "sentiment_intensity",
                    "primary_impact", "business_impacts"
                ]
            )

            # Sort by time (newest first)
            all_news.sort(key=lambda x: x.get('publish_time', 0), reverse=True)
            
            logger.info(f"✅ Found {len(all_news)} news items for {ticker} in last {days} days")
        except Exception as e:
            logger.error(f"❌ Failed to query company news: {e}")
            return {"error": f"Query failed: {str(e)}"}
        
        if not all_news:
            logger.warning(f"⚠️  No news found for {ticker} in last {days} days")
            return {"error": f"No news found for {ticker} in last {days} days"}
        
        # 3. Statistics overview
        event_types = {}
        sentiments = {}
        impacts = {}
        recent_headlines = []
        
        for news in all_news:
            et = news.get('event_type', 'unknown')
            sp = news.get('sentiment_polarity', 'unknown')
            pi = news.get('primary_impact', 'unknown')
            
            event_types[et] = event_types.get(et, 0) + 1
            sentiments[sp] = sentiments.get(sp, 0) + 1
            impacts[pi] = impacts.get(pi, 0) + 1
            
            if len(recent_headlines) < 10:
                recent_headlines.append({
                    'headline': news.get('headline', ''),
                    'time': datetime.fromtimestamp(news.get('publish_time', 0)).strftime('%Y-%m-%d') if news.get('publish_time') else 'Unknown',
                    'sentiment': sp,
                    'impact': pi,
                    'url': news.get('url', '')
                })
        
        # 4. Build company analysis Prompt using YAML template
        logger.info("\n📝 Building company analysis Prompt...")
        
        # Get template configuration
        template_config = self.prompt_loader.get_config('company_analysis')
        max_recent = template_config.get('max_recent_headlines', 5)
        max_representative = template_config.get('max_representative_news', 12)
        headline_max_len = template_config.get('headline_max_length', 100)
        summary_max_len = template_config.get('summary_max_length', 200)
        per_type = template_config.get('representative_per_type', 2)
        
        # Build company information
        company_info = f"""【Company Information】
Stock Ticker: {ticker}
Company Name: {company_name or ticker}
Analysis Time: {now.strftime('%Y-%m-%d %H:%M')}
Analysis Period: Last {days} days ({start_time.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')})
"""
        
        # Build news overview
        news_overview = f"""
【News Data Overview】
Total News: {len(all_news)} items
Event Type Distribution: {', '.join([f'{k}: {v} items' for k, v in sorted(event_types.items(), key=lambda x: x[1], reverse=True)])}
Sentiment Distribution: {', '.join([f'{k}: {v} items' for k, v in sorted(sentiments.items(), key=lambda x: x[1], reverse=True)])}
Impact Type Distribution: {', '.join([f'{k}: {v} items' for k, v in sorted(impacts.items(), key=lambda x: x[1], reverse=True)])}
"""
        
        # Build recent news section (condensed version)
        recent_headlines_limited = recent_headlines[:max_recent]
        recent_news_text = "\n".join([
            f"- [{h['time']}] {h['headline'][:headline_max_len]}... (Sentiment: {h['sentiment']}, Impact: {h['impact']})"
            for h in recent_headlines_limited
        ])
        
        recent_news_section = f"""
【Last {max_recent} News Headlines】
{recent_news_text}
"""
        
        # Select representative news
        representative_news = []
        selected_ids = set()
        
        by_event_type = {}
        for news in all_news:
            et = news.get('event_type', 'other')
            if et not in by_event_type:
                by_event_type[et] = []
            by_event_type[et].append(news)
        
        for et, news_list in by_event_type.items():
            for news in news_list[:per_type]:
                if news['id'] not in selected_ids:
                    representative_news.append(news)
                    selected_ids.add(news['id'])
        
        # Build representative news text (condensed version)
        representative_text = "\n".join([
            f"""
【News {i+1}】
Headline: {news.get('headline', '')[:headline_max_len]}
Time: {datetime.fromtimestamp(news.get('publish_time', 0)).strftime('%Y-%m-%d') if news.get('publish_time') else 'Unknown'}
Summary: {news.get('summary', '')[:summary_max_len]}
Event Type: {news.get('event_type', '')}
Sentiment: {news.get('sentiment_polarity', '')} ({news.get('sentiment_intensity', '')})
Primary Impact: {news.get('primary_impact', '')}
URL: {news.get('url', '')}
"""
            for i, news in enumerate(representative_news[:max_representative])
        ])
        
        # Render Prompt using YAML template
        prompt = self.prompt_loader.render_template(
            'company_analysis',
            ticker=ticker,
            company_name=company_name or ticker,
            days=days,
            analysis_date=now.strftime('%Y-%m-%d'),
            total_news=len(all_news),
            company_info=company_info,
            news_overview=news_overview,
            recent_news_section=recent_news_section,
            representative_text=representative_text
        )
        
        # 5. Call LLM for analysis
        logger.info("\n🤖 Calling LLM for comprehensive company analysis...")
        llm_result = self.llm_client.generate_impact_analysis(
            prompt=prompt,
            temperature=temperature
        )
        
        # Parse LLM returned raw_response
        logger.info("\n📝 Parsing LLM response...")
        if 'raw_response' in llm_result:
            json_convertor_module = importlib.import_module('09_retrieve.json_convertor')
            parse_llm_raw_response = json_convertor_module.parse_llm_raw_response
            parsed_llm = parse_llm_raw_response(llm_result['raw_response'])
            
            if parsed_llm:
                logger.info("✅ LLM response parsing successful")
                logger.info(f"   Parsed fields: {list(parsed_llm.keys())}")
            else:
                logger.warning("⚠️  LLM response parsing failed, using raw result")
                parsed_llm = llm_result
        else:
            logger.warning("⚠️  No raw_response field in LLM result")
            parsed_llm = llm_result
        
        # 6. Merge results
        final_result = {
            'ticker': ticker,
            'company_name': company_name,
            'analysis_period_days': days,
            'start_date': start_time.strftime('%Y-%m-%d'),
            'end_date': now.strftime('%Y-%m-%d'),
            'total_news': len(all_news),
            'news_overview': {
                'event_types': event_types,
                'sentiments': sentiments,
                'impacts': impacts,
                'recent_headlines': recent_headlines
            },
            'llm_analysis': parsed_llm,
            'analysis_complete': True,
            'all_news_urls': [news.get('url') for news in all_news if news.get('url')]
        }
        
        # 7. Automatically evaluate analysis quality
        logger.info("\n📊 Starting quality evaluation...")
        evaluator = AnalysisEvaluator()
        quality_report = evaluator.evaluate_analysis(parsed_llm)
        final_result['quality_evaluation'] = quality_report
        
        logger.info(f"✅ Quality evaluation complete - Total Score: {quality_report['overall_score']:.2f}, Grade: {quality_report['grade']}")
        logger.info("="*70)
        
        return final_result

    def extract_context_for_llm(self, results: List[Dict], max_length: int = 2000) -> str:
        """Extract context suitable for LLM"""
        contexts = []
        current_length = 0

        for news in results:
            publish_time = news.get('publish_time', 0)
            time_str = datetime.fromtimestamp(publish_time).strftime('%Y-%m-%d') if publish_time else 'Unknown'

            context = f"Headline: {news.get('headline', '')}\n"
            context += f"Ticker: {news.get('ticker', '')}\n"
            context += f"Time: {time_str}\n"

            if news.get('summary'):
                context += f"Summary: {news['summary']}\n"

            context += f"Sentiment: {news.get('sentiment_polarity', '')}\n"
            context += f"Event Type: {news.get('event_type', '')}\n"
            context += "---\n"

            if current_length + len(context) > max_length:
                break

            contexts.append(context)
            current_length += len(context)

        return "\n".join(contexts)

    def format_results(self, results: List[Dict]) -> str:
        """Format search results"""
        if not results:
            return "No relevant results found"

        output = []
        output.append(f"\n{'='*70}")
        output.append(f"📊 Search Results (Total: {len(results)} items)")
        output.append(f"{'='*70}\n")

        for i, news in enumerate(results, 1):
            publish_time = news.get('publish_time', 0)
            time_str = datetime.fromtimestamp(publish_time).strftime('%Y-%m-%d %H:%M') if publish_time else "Unknown"

            output.append(f"[{i}] {news.get('headline', 'N/A')}")
            output.append(f"    📈 Ticker: {news.get('ticker', 'N/A')}")
            output.append(f"    🏭 Industry: {news.get('industry', 'N/A')}")
            output.append(f"    📋 Event: {news.get('event_type', 'N/A')}")
            output.append(f"    😊 Sentiment: {news.get('sentiment_polarity', 'N/A')}")
            output.append(f"    📅 Time: {time_str}")

            if 'final_rank_score' in news:
                output.append(f"    🎯 Score: {news['final_rank_score']:.4f}")
            elif 'similarity' in news:
                output.append(f"    🎯 Similarity: {news['similarity']:.4f}")
            elif 'keyword_score' in news:
                output.append(f"    🎯 Keyword Match: {news['keyword_score']}")

            # Add URL (if exists)
            if news.get('url'):
                output.append(f"    🔗 URL: {news['url']}")

            output.append("")

        return "\n".join(output)
