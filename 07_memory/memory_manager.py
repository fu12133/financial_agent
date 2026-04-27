"""
Memory Manager - Unified management of short-term and long-term memory
"""
import sys
import os
import logging
import uuid
import importlib
from typing import Dict, List, Optional, Any

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules
_memory_types_module = importlib.import_module('07_memory.memory_types')
MemoryItem = _memory_types_module.MemoryItem
MemoryCategory = _memory_types_module.MemoryCategory
MemoryType = _memory_types_module.MemoryType

_short_term_module = importlib.import_module('07_memory.short_term_memory')
ShortTermMemory = _short_term_module.ShortTermMemory

_long_term_module = importlib.import_module('07_memory.long_term_memory')
LongTermMemory = _long_term_module.LongTermMemory

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Memory Manager
    - Unified management of short-term and long-term memory
    - Provide simple API interface
    - Automatic decision on memory storage location
    """

    def __init__(self, user_id: str = "default"):
        """
        Initialize memory manager

        Args:
            user_id: User ID
        """
        self.user_id = user_id
        self.session_id = None

        # Initialize short-term memory
        self.short_term = ShortTermMemory()

        # Initialize long-term memory
        self.long_term = LongTermMemory(user_id=user_id)

        logger.info(f"✅ Memory manager initialized successfully (User: {user_id})")

    def start_session(self, session_id: str = None) -> str:
        """
        Start new session

        Args:
            session_id: Session ID, auto-generated if not provided

        Returns:
            Session ID
        """
        self.session_id = self.short_term.create_session(session_id)
        logger.info(f"🚀 Started session: {self.session_id[:8]}...")
        return self.session_id

    def end_session(self) -> bool:
        """
        End current session

        Returns:
            Whether successful
        """
        if self.session_id:
            result = self.short_term.clear_session(self.session_id)
            logger.info(f"🔚 Ended session: {self.session_id[:8]}...")
            self.session_id = None
            return result
        return False

    def remember(self, content: str,
                category: MemoryCategory,
                memory_type: MemoryType = None,
                metadata: Dict[str, Any] = None,
                importance: float = 0.5,
                tags: List[str] = None,
                **kwargs) -> str:
        """
        Remember something (automatically choose storage location)

        Args:
            content: Memory content
            category: Memory category
            memory_type: Memory type, None for automatic judgment
            metadata: Metadata
            importance: Importance (0-1)
            tags: Tag list
            **kwargs: Other parameters

        Returns:
            Memory ID
        """
        # Automatically determine memory type
        if memory_type is None:
            # High importance or specific categories use long-term memory
            if importance > 0.7 or category in [
                MemoryCategory.USER_PREFERENCE,
                MemoryCategory.COMPANY_ANALYSIS,
                MemoryCategory.WATCHLIST
            ]:
                memory_type = MemoryType.LONG_TERM
            else:
                memory_type = MemoryType.SHORT_TERM

        # Store memory
        if memory_type == MemoryType.SHORT_TERM:
            if not self.session_id:
                self.start_session()

            return self.short_term.add_memory(
                session_id=self.session_id,
                content=content,
                category=category,
                metadata=metadata,
                importance=importance,
                tags=tags
            )
        else:
            return self.long_term.add_memory(
                content=content,
                category=category,
                metadata=metadata,
                importance=importance,
                tags=tags,
                source=kwargs.get('source', '')
            )

    def recall(self, query: str,
              memory_type: MemoryType = None,
              category: MemoryCategory = None,
              limit: int = 10,
              **kwargs) -> List[MemoryItem]:
        """
        Recall (retrieve memories)

        Args:
            query: Query content
            memory_type: Memory type, None for retrieving both types
            category: Filter by category
            limit: Return count
            **kwargs: Other parameters

        Returns:
            Memory list
        """
        results = []

        if memory_type in [None, MemoryType.SHORT_TERM]:
            if self.session_id:
                # Short-term memory: keyword search
                short_results = self.short_term.search_memories(
                    session_id=self.session_id,
                    keyword=query,
                    limit=limit
                )
                results.extend(short_results)

        if memory_type in [None, MemoryType.LONG_TERM]:
            # Long-term memory: prioritize semantic search
            if kwargs.get('use_semantic', True):
                long_results = self.long_term.search_by_similarity(
                    query=query,
                    limit=limit,
                    threshold=kwargs.get('threshold', 0.7)
                )
            else:
                long_results = self.long_term.search_by_keyword(
                    keyword=query,
                    category=category,
                    limit=limit
                )
            results.extend(long_results)

        # Sort by importance
        results.sort(key=lambda x: x.importance, reverse=True)

        logger.info(f"🔍 Memory retrieval found {len(results)} memories")
        return results[:limit]

    def forget(self, memory_id: str,
              memory_type: MemoryType = None) -> bool:
        """
        Forget (delete memory)

        Args:
            memory_id: Memory ID
            memory_type: Memory type, None to try both types

        Returns:
            Whether deletion was successful
        """
        if memory_type in [None, MemoryType.SHORT_TERM]:
            if self.session_id:
                if self.short_term.delete_memory(self.session_id, memory_id):
                    return True

        if memory_type in [None, MemoryType.LONG_TERM]:
            if self.long_term.delete_memory(memory_id):
                return True

        return False

    def get_context(self, query: str = None, limit: int = 5) -> str:
        """
        Get context (for LLM prompt)

        Args:
            query: Related query
            limit: Memory count

        Returns:
            Formatted context string
        """
        if query:
            memories = self.recall(query, limit=limit)
        else:
            # Get recent memories
            if self.session_id:
                memories = self.short_term.get_recent_memories(
                    self.session_id,
                    limit=limit
                )
            else:
                memories = []

        if not memories:
            return "No relevant historical memories"

        # Format context
        context_lines = ["【Historical Memories】"]
        for i, memory in enumerate(memories, 1):
            context_lines.append(f"{i}. [{memory.category.value}] {memory.content[:200]}")

        return "\n".join(context_lines)

    def save_analysis_result(self, ticker: str,
                            company_name: str,
                            analysis_summary: str,
                            report_path: str = "",
                            importance: float = 0.8):
        """
        Save company analysis result to long-term memory

        Args:
            ticker: Stock ticker
            company_name: Company name
            analysis_summary: Analysis summary
            report_path: Report path
            importance: Importance
        """
        content = f"{company_name} ({ticker}): {analysis_summary}"

        memory_id = self.remember(
            content=content,
            category=MemoryCategory.COMPANY_ANALYSIS,
            memory_type=MemoryType.LONG_TERM,
            importance=importance,
            tags=[ticker, company_name],
            metadata={
                "ticker": ticker,
                "company_name": company_name
            },
            source=report_path
        )

        logger.info(f"💾 Saved analysis result to long-term memory: {memory_id[:8]}...")
        return memory_id

    def get_watchlist(self) -> List[str]:
        """
        Get watchlist

        Returns:
            Stock ticker list
        """
        memories = self.long_term.get_user_memories(
            category=MemoryCategory.WATCHLIST,
            limit=100
        )

        tickers = []
        for memory in memories:
            if hasattr(memory, 'metadata') and isinstance(memory.metadata, dict):
                ticker = memory.metadata.get('ticker')
                if ticker:
                    tickers.append(ticker)

        return tickers

    def add_to_watchlist(self, ticker: str, company_name: str = ""):
        """
        Add to watchlist

        Args:
            ticker: Stock ticker
            company_name: Company name
        """
        content = f"Watch stock: {company_name} ({ticker})" if company_name else f"Watch stock: {ticker}"

        self.remember(
            content=content,
            category=MemoryCategory.WATCHLIST,
            memory_type=MemoryType.LONG_TERM,
            importance=0.9,
            tags=[ticker],
            metadata={"ticker": ticker, "company_name": company_name}
        )

        logger.info(f"📌 Added to watchlist: {ticker}")

    def close(self):
        """Close all connections"""
        self.long_term.close()