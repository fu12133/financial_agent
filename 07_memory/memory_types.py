"""
Memory Type Definitions
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


class MemoryType(Enum):
    """Memory type enumeration"""
    SHORT_TERM = "short_term"      # Short-term memory
    LONG_TERM = "long_term"        # Long-term memory


class MemoryCategory(Enum):
    """Memory categories"""
    USER_PREFERENCE = "user_preference"     # User preferences
    COMPANY_ANALYSIS = "company_analysis"   # Company analysis
    MARKET_EVENT = "market_event"           # Market events
    CONVERSATION = "conversation"           # Conversation history
    INSIGHT = "insight"                     # Insights and discoveries
    WATCHLIST = "watchlist"                 # Watchlist


@dataclass
class MemoryItem:
    """Memory item data structure"""
    id: str                                 # Memory ID
    content: str                            # Memory content
    category: MemoryCategory                # Category
    metadata: Dict[str, Any] = field(default_factory=dict)  # Metadata
    importance: float = 0.5                 # Importance score (0-1)
    created_at: datetime = field(default_factory=datetime.now)  # Creation time
    updated_at: datetime = field(default_factory=datetime.now)  # Update time
    access_count: int = 0                   # Access count
    tags: List[str] = field(default_factory=list)  # Tags

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category.value,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            content=data["content"],
            category=MemoryCategory(data["category"]),
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data["updated_at"], str) else data["updated_at"],
            access_count=data.get("access_count", 0),
            tags=data.get("tags", [])
        )


@dataclass
class ShortTermMemoryItem(MemoryItem):
    """Short-term memory item"""
    session_id: str = ""                    # Session ID
    expires_at: Optional[datetime] = None   # Expiration time

    def is_expired(self) -> bool:
        """Check if expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False


@dataclass
class LongTermMemoryItem(MemoryItem):
    """Long-term memory item"""
    user_id: str = "default"               # User ID
    embedding: Optional[List[float]] = None  # Vector embedding
    source: str = ""                        # Source (e.g., report path)
