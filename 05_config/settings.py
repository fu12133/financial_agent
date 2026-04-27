"""
Unified Configuration Management
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """System configuration class"""
    
    # ========== Milvus Configuration ==========
    MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
    COLLECTION_NAME = "financial_news_enhanced"
    VECTOR_DIMENSION = 1024  # BGE-M3 dimension
    DUPLICATE_THRESHOLD = 0.95  # Deduplication similarity threshold
    
    # ========== MySQL Configuration ==========
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "your_password"),
        "db": os.getenv("DB_NAME", "financial_agent"),
        "charset": "utf8mb4"
    }
    
    # ========== Vector Model Configuration ==========
    # BGE-M3 local model snapshot directory (embedding.py will automatically find specific snapshot)
    _hf_home = os.getenv("HF_HOME", r"I:\Model\huggingface")
    EMBEDDING_MODEL = os.path.join(
        _hf_home, 
        "hub", 
        "models--BAAI--bge-m3", 
        "snapshots"
    )
    
    # ========== Processing Parameters ==========
    BATCH_SIZE = 50
    DEFAULT_DAYS = 30
    SEARCH_THRESHOLD = 0.7
    SEARCH_LIMIT = 10
    
    # ========== Popular Stock List ==========
    POPULAR_TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
        "META", "NVDA", "JPM", "BAC", "WMT"
    ]
    
    # ==================== LLM Configuration ====================
    # Default LLM model (for automatic detection)
    DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "qwen-plus")
    
    # Ollama Configuration (local)
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # Hugging Face Transformers Configuration (local)
    HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
    HF_MAX_NEW_TOKENS = int(os.getenv("HF_MAX_NEW_TOKENS", "4096"))
    
    # Cloud LLM Configuration
    QWEN_CLOUD_MODEL = os.getenv("QWEN_CLOUD_MODEL", "qwen-plus")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    
    # LLM Generation Configuration
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    # Separate max token count for cloud and local
    CLOUD_LLM_MAX_TOKENS = int(os.getenv("CLOUD_LLM_MAX_TOKENS", "8192"))
    LOCAL_LLM_MAX_TOKENS = int(os.getenv("LOCAL_LLM_MAX_TOKENS", "4096"))
    
    # Compatible with old configuration
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "8192"))
    
    # Company analysis configuration
    ANALYSIS_DAYS = int(os.getenv("ANALYSIS_DAYS", "7"))

    @classmethod
    def get_device(cls) -> str:
        """Automatically detect device (lazy import)"""
        try:
            import torch
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        except ImportError:
            return 'cpu'
