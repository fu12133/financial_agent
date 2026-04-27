"""
RAG Retriever - Supports BM25 + Vector Hybrid Retrieval + Rerank + Impact Analysis
"""
import sys
import os
import logging
import importlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import re

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules starting with numbers
pipeline_module = importlib.import_module('08_pipeline.embedding')
EmbeddingEngine = pipeline_module.EmbeddingEngine

storage_module = importlib.import_module('10_storage.milvus_manager')
MilvusManager = storage_module.MilvusManager

config_module = importlib.import_module('05_config.settings')
Config = config_module.Config

try:
    from rank_bm25 import BM25Okapi
    import jieba
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retriever - Vector retrieval + BM25 keyword retrieval"""

    def __init__(self, device: str = None):
        self.embedding_engine = EmbeddingEngine(device=device)
        self.vector_db = MilvusManager()
        self.bm25_index = None
        self.documents = []
        self.doc_ids = []
        
        if not BM25_AVAILABLE:
            logger.warning("⚠️  rank_bm25 or jieba not installed")

    def _tokenize_chinese(self, text: str) -> List[str]:
        """Chinese text tokenization"""
        if not BM25_AVAILABLE:
            return text.split()
        return list(jieba.cut(text))

    def build_bm25_index_from_milvus(self, limit: int = 1000):
        """Load data from Milvus and build BM25 index"""
        if not BM25_AVAILABLE:
            logger.error("❌ BM25 functionality unavailable, please install dependencies: pip install rank-bm25 jieba")
            raise ImportError("BM25 functionality requires rank-bm25 and jieba libraries")
        
        logger.info(f"📥 Loading data from Milvus to build BM25 index...")
        
        # Use query method to get all documents (not search)
        try:
            all_docs = self.vector_db.client.query(
                collection_name=self.vector_db.collection_name,
                filter="id > 0",  # Get all records with ID > 0
                limit=limit,
                output_fields=[
                    "id", "ticker", "headline", "summary", "url", "source",
                    "publish_time", "event_type", "industry", 
                    "sentiment_polarity", "sentiment_intensity",
                    "primary_impact", "business_impacts"
                ]
            )
        except Exception as e:
            logger.error(f"❌ Failed to fetch data from Milvus: {e}")
            raise
        
        if not all_docs:
            logger.warning("⚠️  No data in Milvus, cannot build BM25 index")
            logger.warning("💡 Please run news collection task to populate data:")
            logger.warning("   python 10_storage/news_collector_service.py --run-now")
            logger.warning("   or")
            logger.warning("   python populate_test_data.py")
            return
        
        logger.info(f"✅ Loaded {len(all_docs)} documents from Milvus")
        
        self.documents = all_docs
        self.doc_ids = [doc.get('id') for doc in all_docs]
        
        # Tokenize documents
        tokenized_docs = []
        empty_count = 0
        
        for doc in all_docs:
            headline = doc.get('headline', '')
            summary = doc.get('summary', '')
            text = f"{headline} {summary}".strip()
            
            if not text:
                empty_count += 1
                continue
            
            tokens = self._tokenize_chinese(text)
            if tokens:  # Ensure tokenization result is not empty
                tokenized_docs.append(tokens)
        
        if empty_count > 0:
            logger.warning(f"⚠️  Skipped {empty_count} empty documents")
        
        if not tokenized_docs:
            logger.error("❌ No valid documents to build BM25 index")
            logger.error("💡 Please ensure Milvus contains news data with headlines or summaries")
            return
        
        # Create BM25 index
        try:
            self.bm25_index = BM25Okapi(tokenized_docs)
            logger.info(f"✅ BM25 index built successfully, valid documents: {len(tokenized_docs)}")
        except Exception as e:
            logger.error(f"❌ BM25 index building failed: {e}")
            raise

    def vector_retrieval(self, query: str, 
                        event_type: str = "",
                        industry: str = "",
                        sentiment: str = "",
                        ticker: str = "",
                        top_k: int = 20) -> List[Dict]:
        """
        Vector retrieval:召回 semantically similar, same-type events, historical analogies, sentiment-related news
        
        Args:
            query: Query text
            event_type: Event type filter (same-type events)
            industry: Industry filter
            sentiment: Sentiment filter (sentiment association)
            ticker: Stock ticker
            top_k: Recall quantity
            
        Returns:
            Vector retrieval results
        """
        logger.info(f"🔍 Vector retrieval: '{query}'")
        
        query_vector = self.embedding_engine.encode_news(query, "")
        
        filters = {}
        if event_type:
            filters['event_type'] = event_type
        if industry:
            filters['industry'] = industry
        if sentiment:
            filters['sentiment'] = sentiment
        
        results = self.vector_db.search_with_filters(
            query_vector=query_vector,
            limit=top_k,
            **filters
        )
        
        # Add retrieval source tag to each result
        for result in results:
            result['retrieval_source'] = 'vector'
            result['vector_score'] = result.get('similarity', 0)
        
        logger.info(f"✅ Vector retrieval recalled {len(results)} items")
        return results

    def bm25_retrieval(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        BM25 keyword retrieval:召回 precise events, policy clauses, financial report details, regulatory original text
        
        Args:
            query: Query text
            top_k: Recall quantity
            
        Returns:
            BM25 retrieval results
        """
        if not BM25_AVAILABLE or self.bm25_index is None:
            logger.warning("⚠️  BM25 index not built, skipping BM25 retrieval")
            return []
        
        logger.info(f"🔍 BM25 retrieval: '{query}'")
        
        # Tokenize query
        query_tokens = self._tokenize_chinese(query)
        
        # Get BM25 scores
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top-k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        doc_map = {doc['id']: doc for doc in self.documents}
        
        for idx in top_indices:
            if scores[idx] > 0 and idx < len(self.doc_ids):
                doc_id = self.doc_ids[idx]
                if doc_id in doc_map:
                    result = doc_map[doc_id].copy()
                    result['retrieval_source'] = 'bm25'
                    result['bm25_score'] = float(scores[idx])
                    results.append(result)
        
        logger.info(f"✅ BM25 retrieval recalled {len(results)} items")
        return results

    def merge_and_deduplicate(self, vector_results: List[Dict], 
                             bm25_results: List[Dict]) -> List[Dict]:
        """
        Merge and deduplicate: Deduplicate based on news ID, keep highest score
        
        Args:
            vector_results: Vector retrieval results
            bm25_results: BM25 retrieval results
            
        Returns:
            Merged and deduplicated results
        """
        logger.info(f"🔄 Merge and deduplicate: Vector{len(vector_results)} + BM25{len(bm25_results)}")
        
        merged = {}
        
        # First add vector retrieval results
        for result in vector_results:
            doc_id = result.get('id')
            merged[doc_id] = result.copy()
        
        # Then add BM25 results, keep higher score if already exists
        for result in bm25_results:
            doc_id = result.get('id')
            if doc_id in merged:
                # Already exists, mark as dual source
                merged[doc_id]['retrieval_source'] = 'both'
                merged[doc_id]['bm25_score'] = result.get('bm25_score', 0)
            else:
                merged[doc_id] = result.copy()
        
        results_list = list(merged.values())
        logger.info(f"✅ After merge and deduplication: {len(results_list)} items")
        
        return results_list

    def rerank(self, results: List[Dict], 
              query: str,
              vector_weight: float = 0.7,
              bm25_weight: float = 0.3) -> List[Dict]:
        """
        Reranking: Combine vector scores and BM25 scores for re-ranking
        
        Args:
            results: Merged results
            query: Query text
            vector_weight: Vector weight (default 0.7)
            bm25_weight: BM25 weight (default 0.3)
            
        Returns:
            Re-ranked results
        """
        logger.info(f"🎯 Reranking (vector={vector_weight}, bm25={bm25_weight})")

    def hybrid_retrieval(self, query: str,
                        event_type: str = "",
                        industry: str = "",
                        sentiment: str = "",
                        ticker: str = "",
                        vector_top_k: int = 20,
                        bm25_top_k: int = 20,
                        final_top_k: int = 10,
                        vector_weight: float = 0.7,
                        bm25_weight: float = 0.3) -> List[Dict]:
        """
        Complete hybrid retrieval process: Vector retrieval + BM25 retrieval → Merge and deduplicate → Rerank
        
        Args:
            query: Query text
            event_type: Event type
            industry: Industry
            sentiment: Sentiment
            ticker: Stock ticker
            vector_top_k: Vector retrieval recall quantity
            bm25_top_k: BM25 retrieval recall quantity
            final_top_k: Final return quantity
            vector_weight: Vector weight (default 0.7)
            bm25_weight: BM25 weight (default 0.3)
            
        Returns:
            Final ranked results
        """
        logger.info("="*70)
        logger.info(f"🚀 Starting hybrid retrieval: '{query}'")
        logger.info("="*70)
        
        # 1. Vector retrieval
        vector_results = self.vector_retrieval(
            query, 
            event_type=event_type,
            industry=industry,
            sentiment=sentiment,
            top_k=vector_top_k
        )
        
        # 2. BM25 retrieval
        bm25_results = self.bm25_retrieval(query, top_k=bm25_top_k)
        
        # 3. Merge and deduplicate
        merged_results = self.merge_and_deduplicate(vector_results, bm25_results)
        
        # 4. Rerank
        ranked_results = self.rerank(
            merged_results, 
            query,
            vector_weight=vector_weight,
            bm25_weight=bm25_weight
        )
        
        # 5. Return Top-K
        final_results = ranked_results[:final_top_k]
        
        logger.info(f"✅ Hybrid retrieval completed, returning {len(final_results)} items")
        logger.info("="*70)
        
        return final_results


class ImpactAnalyzer:
    """5-dimensional impact analyzer"""
    
    IMPACT_DIMENSIONS = [
        "Financial Impact",
        "Operational Impact",
        "Market Impact",
        "Regulatory/Compliance Impact",
        "Strategic Impact"
    ]
    
    @staticmethod
    def build_impact_prompt(current_news: Dict, 
                           retrieved_contexts: List[Dict],
                           all_company_news: List[Dict] = None) -> str:
        """
        Build fixed prompt for 5-dimensional Impact Analysis
        
        Args:
            current_news: Current news to be analyzed
            retrieved_contexts: Retrieved related contexts (Top-K)
            all_company_news: All related news for the company (optional)
            
        Returns:
            Complete prompt
        """
        # Format current news
        publish_time_str = datetime.fromtimestamp(current_news.get('publish_time', 0)).strftime('%Y-%m-%d') if current_news.get('publish_time') else 'Unknown'
        
        current_info = f"""
【Current News】
Title: {current_news.get('headline', '')}
Stock: {current_news.get('ticker', '')}
Time: {publish_time_str}
Summary: {current_news.get('summary', '')}
Event Type: {current_news.get('event_type', '')}
Industry: {current_news.get('industry', '')}
Sentiment: {current_news.get('sentiment_polarity', '')} ({current_news.get('sentiment_intensity', '')})
"""
        
        # If there's all company news, add statistics
        company_history_info = ""
        if all_company_news and len(all_company_news) > 0:
            # Count event type distribution
            event_types = {}
            sentiments = {}
            for news in all_company_news:
                et = news.get('event_type', 'unknown')
                sp = news.get('sentiment_polarity', 'unknown')
                event_types[et] = event_types.get(et, 0) + 1
                sentiments[sp] = sentiments.get(sp, 0) + 1
            
            company_history_info = f"""
【{current_news.get('ticker', '')} Historical News Overview】
Total News: {len(all_company_news)} items
Event Type Distribution: {', '.join([f'{k}: {v} items' for k, v in sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:5]])}
Sentiment Distribution: {', '.join([f'{k}: {v} items' for k, v in sorted(sentiments.items(), key=lambda x: x[1], reverse=True)])}

"""
        
        # Format retrieved contexts (most relevant Top-K)
        context_parts = []
        for i, ctx in enumerate(retrieved_contexts, 1):
            ctx_publish_time = datetime.fromtimestamp(ctx.get('publish_time', 0)).strftime('%Y-%m-%d') if ctx.get('publish_time') else 'Unknown'
            
            context_info = f"""
【Related News {i}】
Title: {ctx.get('headline', '')}
Stock: {ctx.get('ticker', '')}
Time: {ctx_publish_time}
Summary: {ctx.get('summary', '')}
Event Type: {ctx.get('event_type', '')}
Sentiment: {ctx.get('sentiment_polarity', '')}
Similarity: {ctx.get('final_rank_score', ctx.get('similarity', 0)):.4f}
"""
            # Add URL (if exists)
            if ctx.get('url'):
                context_info += f"URL: {ctx['url']}\n"
            
            context_parts.append(context_info)
        
        contexts_text = "\n".join(context_parts) if context_parts else "No related historical news"
        
        # Build complete prompt
        prompt = f"""{{%-set enable_thinking = false%}}
You are a professional financial analyst. Please conduct 5-dimensional impact analysis based on the following information.

{current_info}
{company_history_info}
【Retrieved Related Background Information (Top-{len(retrieved_contexts)} Most Relevant)】
{contexts_text}

【Analysis Task】
Please conduct in-depth analysis of the current news from the following 5 dimensions:

1. **Financial Impact**
   - Impact on revenue, profit, cash flow
   - Cost structure changes
   - Financial risk assessment

2. **Operational Impact**
   - Supply chain impact
   - Production efficiency changes
   - Human resources impact
   - Technology/system impact

3. **Market Impact**
   - Short-term/long-term stock price trend prediction
   - Market share changes
   - Competitive landscape impact
   - Investor sentiment

4. **Regulatory/Compliance Impact**
   - Policy and regulatory risks
   - Compliance costs
   - Litigation risks
   - Government relations

5. **Strategic Impact**
   - Long-term competitive advantages
   - Business transformation needs
   - Partnership relationships
   - Market positioning changes

【Output Format】
Please output analysis results in the following JSON format. **Important: In the analysis field of each dimension, you must cite relevant news URLs as evidence support**.

{{
  "financial_impact": {{
    "score": Integer from -10 to 10,
    "analysis": "Detailed analysis, must cite relevant URLs in text, e.g., [Reference: URL]",
    "key_factors": ["Factor 1", "Factor 2"],
    "source_urls": ["Relevant URL 1", "Relevant URL 2"]
  }},
  "operational_impact": {{
    "score": Integer from -10 to 10,
    "analysis": "Detailed analysis, must cite relevant URLs in text",
    "key_factors": ["Factor 1", "Factor 2"],
    "source_urls": ["Relevant URL 1", "Relevant URL 2"]
  }},
  "market_impact": {{
    "score": Integer from -10 to 10,
    "analysis": "Detailed analysis, must cite relevant URLs in text",
    "key_factors": ["Factor 1", "Factor 2"],
    "source_urls": ["Relevant URL 1", "Relevant URL 2"]
  }},
  "regulatory_impact": {{
    "score": Integer from -10 to 10,
    "analysis": "Detailed analysis, must cite relevant URLs in text",
    "key_factors": ["Factor 1", "Factor 2"],
    "source_urls": ["Relevant URL 1", "Relevant URL 2"]
  }},
  "strategic_impact": {{
    "score": Integer from -10 to 10,
    "analysis": "Detailed analysis, must cite relevant URLs in text",
    "key_factors": ["Factor 1", "Factor 2"],
    "source_urls": ["Relevant URL 1", "Relevant URL 2"]
  }},
  "overall_assessment": {{
    "total_score": Integer from -50 to 50,
    "recommendation": "Buy/Hold/Sell",
    "confidence": Float from 0 to 1,
    "summary": "Overall assessment summary, can cite key URLs",
    "source_urls": ["Key URL 1", "Key URL 2"]
  }}
}}

**Important Notes**:
1. Each dimension must include a source_urls array listing news URLs supporting the analysis
2. Also annotate citations in analysis text using [Reference: URL] format
3. Only use provided news URLs, do not fabricate URLs
4. Conduct trend analysis combining historical news overview
5. Ensure analysis is objective, professional, based on provided factual information.
"""
        
        return prompt

    @staticmethod
    def parse_impact_result(llm_response: str) -> Dict:
        """Parse LLM returned impact analysis result"""
        try:
            # Try to extract JSON
            match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
            else:
                return {"error": "Unable to parse LLM response"}
        except Exception as e:
            logger.error(f"❌ Failed to parse impact analysis result: {e}")
            return {"error": str(e)}


class RAGSearcher:
    """RAG retrieval service - Integrates hybrid retrieval and impact analysis"""

    def __init__(self, device: str = None):
        self.retriever = HybridRetriever(device=device)
        self.analyzer = ImpactAnalyzer()
        
        logger.info("✅ RAG retriever initialized successfully (supports hybrid retrieval + Impact Analysis)")

    def initialize_bm25(self, limit: int = 1000):
        """Initialize BM25 index"""
        self.retriever.build_bm25_index_from_milvus(limit=limit)

    def retrieve_and_analyze(self, current_news: Dict,
                            query: str = "",
                            event_type: str = "",
                            industry: str = "",
                            sentiment: str = "",
                            vector_top_k: int = 15,
                            bm25_top_k: int = 15,
                            final_top_k: int = 10,
                            vector_weight: float = 0.7,
                            bm25_weight: float = 0.3) -> Dict:
        """
        Complete process: Retrieve related contexts → Build prompt → Prepare Impact Analysis
        
        Args:
            current_news: Current news to be analyzed
            query: Query text (if not provided, use news headline + summary)
            event_type: Event type
            industry: Industry
            sentiment: Sentiment
            vector_top_k: Vector retrieval quantity
            bm25_top_k: BM25 retrieval quantity
            final_top_k: Final return quantity
            vector_weight: Vector weight (default 0.7)
            bm25_weight: BM25 weight (default 0.3)
            
        Returns:
            Dictionary containing retrieval results and prompt
        """
        logger.info("\n" + "="*70)
        logger.info("🚀 Starting RAG + Impact Analysis process")
        logger.info(f"   Weight configuration: Dense={vector_weight}, Sparse={bm25_weight}")
        logger.info("="*70)
        
        # If no query provided, use news content
        if not query:
            query = f"{current_news.get('headline', '')} {current_news.get('summary', '')}"
        
        # 1. Hybrid retrieval
        retrieved_contexts = self.retriever.hybrid_retrieval(
            query=query,
            event_type=event_type or current_news.get('event_type', ''),
            industry=industry or current_news.get('industry', ''),
            sentiment=sentiment or current_news.get('sentiment_polarity', ''),
            vector_top_k=vector_top_k,
            bm25_top_k=bm25_top_k,
            final_top_k=final_top_k,
            vector_weight=vector_weight,
            bm25_weight=bm25_weight
        )
        
        # 2. Build Impact Analysis Prompt
        prompt = self.analyzer.build_impact_prompt(current_news, retrieved_contexts)
        
        result = {
            "current_news": current_news,
            "retrieved_contexts": retrieved_contexts,
            "context_count": len(retrieved_contexts),
            "impact_analysis_prompt": prompt,
            "next_step": "Send prompt to LLM for 5-dimensional impact analysis"
        }
        
        logger.info(f"✅ Retrieved {len(retrieved_contexts)} related contexts")
        logger.info(f"✅ Prompt length: {len(prompt)} characters")
        logger.info("="*70)
        
        return result

    def format_retrieval_results(self, results: List[Dict]) -> str:
        """Format retrieval results"""
        if not results:
            return "No related results found"
        
        output = []
        output.append(f"\n{'='*70}")
        output.append(f"📊 Retrieval Results (Total {len(results)} items)")
        output.append(f"{'='*70}\n")
        
        for i, news in enumerate(results, 1):
            publish_time = news.get('publish_time', 0)
            time_str = datetime.fromtimestamp(publish_time).strftime('%Y-%m-%d %H:%M') if publish_time else "Unknown"
            
            output.append(f"[{i}] {news.get('headline', 'N/A')}")
            output.append(f"    📈 Stock: {news.get('ticker', 'N/A')}")
            output.append(f"    📋 Event: {news.get('event_type', 'N/A')}")
            output.append(f"    😊 Sentiment: {news.get('sentiment_polarity', 'N/A')}")
            output.append(f"    📅 Time: {time_str}")
            output.append(f"    🔍 Source: {news.get('retrieval_source', 'unknown')}")
            output.append(f"    🎯 Score: {news.get('final_rank_score', news.get('similarity', 0)):.4f}")
            
            if news.get('url'):
                output.append(f"    🔗 URL: {news['url']}")
            
            if news.get('summary'):
                summary = news['summary'][:150] + "..." if len(news['summary']) > 150 else news['summary']
                output.append(f"    📝 {summary}")
            
            output.append("")
        
        return "\n".join(output)
