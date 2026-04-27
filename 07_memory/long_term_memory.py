"""
Long-term Memory Management - Persistent storage memory
Uses Milvus for vector retrieval + MySQL for structured data storage
"""
import sys
import os
import logging
import uuid
import json
import pymysql
import importlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from pymilvus import DataType

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import modules
_memory_types_module = importlib.import_module('07_memory.memory_types')
LongTermMemoryItem = _memory_types_module.LongTermMemoryItem
MemoryCategory = _memory_types_module.MemoryCategory

_config_module = importlib.import_module('05_config.settings')
Config = _config_module.Config

logger = logging.getLogger(__name__)


class LongTermMemory:
    """
    Long-term memory manager
    - Uses Milvus for vector storage (supports semantic search)
    - Uses MySQL for structured data storage
    - Supports persistence and cross-session access
    """

    def __init__(self, user_id: str = "default"):
        """
        Initialize long-term memory

        Args:
            user_id: User ID
        """
        self.user_id = user_id
        self.collection_name = f"long_term_memory_{user_id}"
        self.embedding_dim = Config.VECTOR_DIMENSION

        # Initialize Milvus connection
        try:
            _storage_module = importlib.import_module('10_storage.milvus_manager')
            MilvusManager = _storage_module.MilvusManager
            # MilvusManager already connects automatically in __init__
            self.milvus = MilvusManager(
                uri=Config.MILVUS_URI,
                collection_name=self.collection_name
            )
            
            # Initialize collection (create if not exists)
            self._init_milvus_collection()
            
            self.use_milvus = True
            logger.info(f"✅ Milvus long-term memory collection ready: {self.collection_name}")
        except Exception as e:
            logger.warning(f"⚠️  Milvus initialization failed, will only use MySQL: {e}")
            self.use_milvus = False

        # Initialize MySQL connection
        try:
            self.mysql_conn = pymysql.connect(**Config.DB_CONFIG)
            self._create_memory_table()
            self.use_mysql = True
            logger.info("✅ MySQL long-term memory table ready")
        except Exception as e:
            logger.error(f"❌ MySQL initialization failed: {e}")
            self.use_mysql = False

        # Initialize vector model
        try:
            _pipeline_module = importlib.import_module('08_pipeline.embedding')
            EmbeddingEngine = _pipeline_module.EmbeddingEngine
            self.embedding_engine = EmbeddingEngine()
            self.use_embedding = True
            logger.info("✅ Vector engine ready")
        except Exception as e:
            logger.warning(f"⚠️  Vector engine initialization failed: {e}")
            self.use_embedding = False

    def _init_milvus_collection(self):
        """Create collection"""
        # Check if collection already exists
        if self.milvus.client.has_collection(self.collection_name):
            logger.info(f"✅ Milvus collection {self.collection_name} already exists, skipping creation")
            return
        
        logger.info(f"🔨 Creating new Milvus collection: {self.collection_name}")
        
        schema = self.milvus.client.create_schema(
            auto_id=False,
            enable_dynamic_field=True
        )
        schema.add_field("id", DataType.VARCHAR, max_length=36, is_primary=True)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=self.embedding_dim)
        schema.add_field("user_id", DataType.VARCHAR, max_length=50)
        schema.add_field("category", DataType.VARCHAR, max_length=50)
        schema.add_field("importance", DataType.INT64)
        # Note: Milvus VARCHAR length is calculated in bytes
        # Chinese characters take 3 bytes, so 1000 bytes ≈ 333 Chinese characters
        # For safety, set to 600 bytes (approximately 200 Chinese characters)
        schema.add_field("content_preview", DataType.VARCHAR, max_length=600)
        
        # Create index
        index_params = self.milvus.client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            metric_type="COSINE",
            index_type="IVF_FLAT",
            params={"nlist": 128}
        )
        
        # Create collection
        self.milvus.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )
        
        # Load collection into memory
        self.milvus.client.load_collection(self.collection_name)
        logger.info(f"✅ Milvus collection {self.collection_name} created successfully")

    def add_memory(self, content: str,
                   category: MemoryCategory,
                   metadata: Dict[str, Any] = None,
                   importance: float = 0.5,
                   tags: List[str] = None,
                   source: str = "") -> str:
        """
        Add long-term memory

        Args:
            content: Memory content
            category: Memory category
            metadata: Metadata
            importance: Importance (0-1)
            tags: Tag list
            source: Source (e.g., report path)

        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())

        # Generate vector embedding
        embedding = None
        if self.use_embedding:
            try:
                result = self.embedding_engine.encode([content])
                embedding = result['dense_vecs'][0].tolist()
            except Exception as e:
                logger.warning(f"⚠️  Vector generation failed: {e}")

        # Create memory item
        memory_item = LongTermMemoryItem(
            id=memory_id,
            content=content,
            category=category,
            metadata=metadata or {},
            importance=importance,
            tags=tags or [],
            user_id=self.user_id,
            embedding=embedding,
            source=source
        )

        # Store in MySQL
        if self.use_mysql:
            self._save_to_mysql(memory_item)

        # Store in Milvus (vector retrieval)
        if self.use_milvus and embedding:
            self._save_to_milvus(memory_item, embedding)

        logger.info(f"💾 Added long-term memory: {memory_id[:8]}... (Category: {category.value})")
        return memory_id

    def search_by_similarity(self, query: str,
                            limit: int = 10,
                            threshold: float = 0.7) -> List[LongTermMemoryItem]:
        """
        Semantic search based on similarity

        Args:
            query: Query text
            limit: Return count
            threshold: Similarity threshold

        Returns:
            Matching memory list
        """
        if not self.use_milvus or not self.use_embedding:
            logger.warning("⚠️  Vector search unavailable")
            return []

        # Generate query vector
        try:
            result = self.embedding_engine.encode([query])
            query_vector = result['dense_vecs'][0].tolist()
        except Exception as e:
            logger.error(f"❌ Query vector generation failed: {e}")
            return []

        # Search in Milvus
        try:
            # Use Milvus client directly for search
            res = self.milvus.client.search(
                collection_name=self.collection_name,
                data=[query_vector],
                limit=limit,
                output_fields=["id", "user_id", "category", "importance", "content_preview"],
                params={"metric_type": "COSINE"}
            )

            # Get complete memory items
            memory_items = []
            if res and len(res) > 0:
                for hit in res[0]:
                    if hit["distance"] >= threshold:
                        memory_id = hit["entity"].get('id')
                        if memory_id:
                            memory = self.get_memory(memory_id)
                            if memory:
                                memory_items.append(memory)

            logger.info(f"🔍 Similarity search found {len(memory_items)} memories")
            return memory_items

        except Exception as e:
            logger.error(f"❌ Vector search failed: {e}")
            return []

    def search_by_keyword(self, keyword: str,
                         category: MemoryCategory = None,
                         limit: int = 10) -> List[LongTermMemoryItem]:
        """
        Keyword search
        
        Args:
            keyword: Search keyword
            category: Filter by category
            limit: Return count
            
        Returns:
            Matching memory list
        """
        if not self.use_mysql:
            return []
        
        try:
            import pymysql
            cursor = self.mysql_conn.cursor(pymysql.cursors.DictCursor)
            
            query = "SELECT * FROM long_term_memories WHERE user_id = %s AND content LIKE %s"
            params = [self.user_id, f"%{keyword}%"]
            
            if category:
                query += " AND category = %s"
                params.append(category.value)
            
            query += " ORDER BY importance DESC, created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            
            memories = [LongTermMemoryItem.from_dict(row) for row in rows]
            logger.info(f"🔍 Keyword search found {len(memories)} memories")
            return memories
            
        except Exception as e:
            logger.error(f"❌ Keyword search failed: {e}")
            return []

    def get_memory(self, memory_id: str) -> Optional[LongTermMemoryItem]:
        """
        Get single memory

        Args:
            memory_id: Memory ID

        Returns:
            Memory item
        """
        if not self.use_mysql:
            return None

        try:
            cursor = self.mysql_conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM long_term_memories WHERE id = %s AND user_id = %s",
                (memory_id, self.user_id)
            )
            row = cursor.fetchone()
            cursor.close()

            if row:
                # Update access count
                self._update_access_count(memory_id)
                return LongTermMemoryItem.from_dict(row)

            return None

        except Exception as e:
            logger.error(f"❌ Failed to get memory: {e}")
            return None

    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete memory

        Args:
            memory_id: Memory ID

        Returns:
            Whether deletion was successful
        """
        success = True

        # Delete from MySQL
        if self.use_mysql:
            try:
                cursor = self.mysql_conn.cursor()
                cursor.execute(
                    "DELETE FROM long_term_memories WHERE id = %s AND user_id = %s",
                    (memory_id, self.user_id)
                )
                self.mysql_conn.commit()
                cursor.close()
            except Exception as e:
                logger.error(f"❌ MySQL deletion failed: {e}")
                success = False

        # Delete from Milvus
        if self.use_milvus:
            try:
                self.milvus.client.delete(
                    collection_name=self.collection_name,
                    filter=f'id == "{memory_id}"'
                )
            except Exception as e:
                logger.error(f"❌ Milvus deletion failed: {e}")
                success = False

        if success:
            logger.info(f"🗑️  Deleted long-term memory: {memory_id[:8]}...")

        return success

    def get_user_memories(self, category: MemoryCategory = None,
                         limit: int = 50) -> List[LongTermMemoryItem]:
        """
        Get all user memories

        Args:
            category: Filter by category
            limit: Return count

        Returns:
            Memory list
        """
        if not self.use_mysql:
            return []

        try:
            cursor = self.mysql_conn.cursor(pymysql.cursors.DictCursor)

            query = "SELECT * FROM long_term_memories WHERE user_id = %s"
            params = [self.user_id]

            if category:
                query += " AND category = %s"
                params.append(category.value)

            query += " ORDER BY importance DESC, created_at DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()

            return [LongTermMemoryItem.from_dict(row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Failed to get user memories: {e}")
            return []

    def _create_memory_table(self):
        """Create memory table"""
        try:
            cursor = self.mysql_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memories (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    metadata JSON,
                    importance FLOAT DEFAULT 0.5,
                    tags JSON,
                    source VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    access_count INT DEFAULT 0,
                    INDEX idx_user_category (user_id, category),
                    INDEX idx_importance (importance),
                    INDEX idx_created (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            self.mysql_conn.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"❌ Failed to create table: {e}")
            raise

    def _save_to_mysql(self, memory: LongTermMemoryItem):
        """Save to MySQL"""
        try:
            cursor = self.mysql_conn.cursor()
            cursor.execute("""
                INSERT INTO long_term_memories 
                (id, user_id, content, category, metadata, importance, tags, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                memory.id,
                memory.user_id,
                memory.content,
                memory.category.value,
                json.dumps(memory.metadata, ensure_ascii=False),
                memory.importance,
                json.dumps(memory.tags, ensure_ascii=False),
                memory.source
            ))
            self.mysql_conn.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"❌ MySQL save failed: {e}")
            raise

    def _save_to_milvus(self, memory: LongTermMemoryItem, embedding: List[float]):
        """Save to Milvus"""
        try:
            # Use insert_batch method
            # Milvus VARCHAR max_length=600 bytes
            # Chinese characters take 3 bytes, so maximum 200 Chinese characters
            # For safety, truncate to 180 characters
            content_preview = memory.content[:180] if len(memory.content) > 180 else memory.content
            
            data = [{
                "id": memory.id,  # Directly use UUID string
                "vector": embedding,
                "user_id": memory.user_id,
                "category": memory.category.value,
                # importance field defined as INT64 in schema, needs conversion
                "importance": int(memory.importance * 100),  # Convert 0-1 float to 0-100 integer
                "content_preview": content_preview
            }]
            self.milvus.insert_batch(data)
        except Exception as e:
            logger.error(f"❌ Milvus save failed: {e}")

    def _update_access_count(self, memory_id: str):
        """Update access count"""
        try:
            cursor = self.mysql_conn.cursor()
            cursor.execute(
                "UPDATE long_term_memories SET access_count = access_count + 1 WHERE id = %s",
                (memory_id,)
            )
            self.mysql_conn.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"❌ Failed to update access count: {e}")

    def close(self):
        """Close connections"""
        if self.use_mysql:
            self.mysql_conn.close()
        # MilvusManager has no disconnect method, client manages connections automatically
