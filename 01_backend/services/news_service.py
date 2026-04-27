"""
News Service Layer
"""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from datetime import datetime

# Add project root directory to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Use importlib to import modules starting with numbers
import importlib
rag_module = importlib.import_module('09_retrieve.rag_service')
RAGService = rag_module.RAGService


class NewsService:
    _instance = None
    _rag_service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_rag_service(self) -> RAGService:
        if self._rag_service is None:
            logger.info("Initialize RAG service")
            self._rag_service = RAGService(device='cuda')
        return self._rag_service

    async def query_news(self, ticker: str, days: int = 7,
                        limit: int = 10) -> Dict[str, Any]:
        try:
            rag = self._get_rag_service()

            loop = asyncio.get_event_loop()
            news_list = await loop.run_in_executor(
                None,
                lambda: rag.search_news(ticker, days=days, limit=limit)
            )

            logger.info(f"News query success: ticker={ticker}, count={len(news_list)}")

            return {
                "success": True,
                "ticker": ticker,
                "count": len(news_list),
                "news": news_list,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"News query failed: {e}")
            return {
                "success": False,
                "ticker": ticker,
                "count": 0,
                "news": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
