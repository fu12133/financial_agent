"""
Short-term Memory Management - Session-level temporary memory
"""
import sys
import os
import logging
import uuid
import importlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import OrderedDict

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules
_memory_types_module = importlib.import_module('07_memory.memory_types')
ShortTermMemoryItem = _memory_types_module.ShortTermMemoryItem
MemoryCategory = _memory_types_module.MemoryCategory

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    Short-term memory manager
    - In-memory storage
    - Supports session isolation
    - Automatic cleanup of expired memories
    """

    def __init__(self, max_items_per_session: int = 100,
                 default_ttl_hours: int = 24):
        """
        Initialize short-term memory

        Args:
            max_items_per_session: Maximum memory items per session
            default_ttl_hours: Default time-to-live (hours)
        """
        self.max_items_per_session = max_items_per_session
        self.default_ttl_hours = default_ttl_hours

        # Session memory storage: {session_id: OrderedDict[memory_id, MemoryItem]}
        self.sessions: Dict[str, OrderedDict] = {}

        logger.info("✅ Short-term memory manager initialized successfully")

    def create_session(self, session_id: str = None) -> str:
        """
        Create new session

        Args:
            session_id: Session ID, auto-generated if not provided

        Returns:
            Session ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.sessions:
            self.sessions[session_id] = OrderedDict()
            logger.info(f"🆕 Created new session: {session_id}")

        return session_id

    def add_memory(self, session_id: str, content: str,
                   category: MemoryCategory,
                   metadata: Dict[str, Any] = None,
                   importance: float = 0.5,
                   ttl_hours: int = None,
                   tags: List[str] = None) -> str:
        """
        Add short-term memory

        Args:
            session_id: Session ID
            content: Memory content
            category: Memory category
            metadata: Metadata
            importance: Importance (0-1)
            ttl_hours: Time-to-live (hours), None uses default
            tags: Tag list

        Returns:
            Memory ID
        """
        if session_id not in self.sessions:
            self.create_session(session_id)

        # Check and clean up expired memories
        self._cleanup_expired(session_id)

        # Create memory item
        memory_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=ttl_hours or self.default_ttl_hours)

        memory_item = ShortTermMemoryItem(
            id=memory_id,
            content=content,
            category=category,
            metadata=metadata or {},
            importance=importance,
            tags=tags or [],
            session_id=session_id,
            expires_at=expires_at
        )

        # Add to session
        session_memories = self.sessions[session_id]

        # If at capacity, remove oldest memory
        if len(session_memories) >= self.max_items_per_session:
            oldest_id = next(iter(session_memories))
            removed = session_memories.pop(oldest_id)
            logger.debug(f"🗑️  Removed expired memory: {oldest_id[:8]}...")

        session_memories[memory_id] = memory_item

        logger.debug(f"💾 Added short-term memory: {memory_id[:8]}... (Session: {session_id[:8]}...)")
        return memory_id

    def get_memory(self, session_id: str, memory_id: str) -> Optional[ShortTermMemoryItem]:
        """
        Get single memory

        Args:
            session_id: Session ID
            memory_id: Memory ID

        Returns:
            Memory item, None if not exists
        """
        if session_id not in self.sessions:
            return None

        memory = self.sessions[session_id].get(memory_id)
        if memory:
            if memory.is_expired():
                del self.sessions[session_id][memory_id]
                return None

            # Update access count
            memory.access_count += 1
            memory.updated_at = datetime.now()

        return memory

    def get_recent_memories(self, session_id: str,
                           limit: int = 10,
                           category: MemoryCategory = None) -> List[ShortTermMemoryItem]:
        """
        Get recent memories

        Args:
            session_id: Session ID
            limit: Return count limit
            category: Filter by category, None returns all

        Returns:
            Memory list (sorted by time descending)
        """
        if session_id not in self.sessions:
            return []

        # Clean up expired memories
        self._cleanup_expired(session_id)

        memories = list(self.sessions[session_id].values())

        # Filter by category
        if category:
            memories = [m for m in memories if m.category == category]

        # Sort by time descending
        memories.sort(key=lambda x: x.created_at, reverse=True)

        return memories[:limit]

    def search_memories(self, session_id: str,
                       keyword: str,
                       limit: int = 10) -> List[ShortTermMemoryItem]:
        """
        Search memories (keyword matching)

        Args:
            session_id: Session ID
            keyword: Search keyword
            limit: Return count limit

        Returns:
            Matching memory list
        """
        if session_id not in self.sessions:
            return []

        self._cleanup_expired(session_id)

        keyword_lower = keyword.lower()
        matched = []

        for memory in self.sessions[session_id].values():
            if (keyword_lower in memory.content.lower() or
                any(keyword_lower in tag.lower() for tag in memory.tags)):
                matched.append(memory)

        # Sort by relevance and time
        matched.sort(key=lambda x: (x.importance, x.created_at), reverse=True)

        return matched[:limit]

    def delete_memory(self, session_id: str, memory_id: str) -> bool:
        """
        Delete memory

        Args:
            session_id: Session ID
            memory_id: Memory ID

        Returns:
            Whether deletion was successful
        """
        if session_id not in self.sessions:
            return False

        if memory_id in self.sessions[session_id]:
            del self.sessions[session_id][memory_id]
            logger.debug(f"🗑️  Deleted memory: {memory_id[:8]}...")
            return True

        return False

    def clear_session(self, session_id: str) -> bool:
        """
        Clear all memories in a session

        Args:
            session_id: Session ID

        Returns:
            Whether clearing was successful
        """
        if session_id in self.sessions:
            count = len(self.sessions[session_id])
            del self.sessions[session_id]
            logger.info(f"🧹 Cleared session {session_id[:8]}... ({count} memories)")
            return True

        return False

    def get_session_stats(self, session_id: str) -> Dict:
        """
        Get session statistics

        Args:
            session_id: Session ID

        Returns:
            Statistics dictionary
        """
        if session_id not in self.sessions:
            return {"exists": False}

        memories = list(self.sessions[session_id].values())

        # Categorize statistics
        category_stats = {}
        for memory in memories:
            cat = memory.category.value
            category_stats[cat] = category_stats.get(cat, 0) + 1

        return {
            "exists": True,
            "total_memories": len(memories),
            "category_distribution": category_stats,
            "avg_importance": sum(m.importance for m in memories) / len(memories) if memories else 0,
            "oldest_memory": min(m.created_at for m in memories).isoformat() if memories else None,
            "newest_memory": max(m.created_at for m in memories).isoformat() if memories else None
        }

    def _cleanup_expired(self, session_id: str):
        """Cleanup expired memories in a session"""
        if session_id not in self.sessions:
            return

        expired_ids = [
            mid for mid, memory in self.sessions[session_id].items()
            if memory.is_expired()
        ]

        for mid in expired_ids:
            del self.sessions[session_id][mid]

        if expired_ids:
            logger.debug(f"🧹 Cleaned up {len(expired_ids)} expired memories")
