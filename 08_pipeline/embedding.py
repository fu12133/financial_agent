"""
Embedding Engine - BGE-M3 Model Wrapper
"""
import sys
import os
import glob
import logging
import importlib
from typing import List
import numpy as np

# Add project root directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Use importlib to import Config (module name starts with number)
config_module = importlib.import_module('05_config.settings')
Config = config_module.Config

# Try to import FlagEmbedding
try:
    from FlagEmbedding import BGEM3FlagModel
    USE_FLAG_EMBEDDING = True
except ImportError:
    USE_FLAG_EMBEDDING = False

# Try to import SentenceTransformer
try:
    from sentence_transformers import SentenceTransformer
    USE_SENTENCE_TRANSFORMER = True
except ImportError:
    USE_SENTENCE_TRANSFORMER = False

# Suppress verbose logs from third-party libraries
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("torch").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """BGE-M3 vector generation engine"""

    def __init__(self, model_name: str = None, device: str = None):
        """
        Initialize embedding engine

        Args:
            model_name: Model name or local path, defaults to Config.EMBEDDING_MODEL
            device: Computing device, 'cuda' or 'cpu', auto-detected by default
        """
        # Prefer passed model_name, otherwise use Config
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = Config.EMBEDDING_MODEL
        
        # Prefer passed device, otherwise auto-detect
        if device:
            self.device = device
        else:
            self.device = Config.get_device()
        
        self.dimension = Config.VECTOR_DIMENSION

        # Set HuggingFace cache directory and environment variables (domestic acceleration)
        hf_home = os.getenv('HF_HOME')
        if hf_home:
            os.environ['HF_HOME'] = hf_home
            logger.info(f"📁 HF_HOME: {hf_home}")
        
        if not os.getenv('HF_ENDPOINT'):
            os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
            logger.info("🌐 Using HuggingFace mirror source")
        
        # If configured as base path (snapshots directory), find actual snapshot
        if os.path.isdir(self.model_name) and 'snapshots' in self.model_name:
            snapshot_dirs = glob.glob(os.path.join(self.model_name, '*'))
            if snapshot_dirs:
                self.model_name = snapshot_dirs[0]
                logger.info(f"📂 Found local snapshot: {self.model_name}")
            else:
                logger.warning(f"⚠️  No snapshot directory found, falling back to model name: BAAI/bge-m3")
                self.model_name = "BAAI/bge-m3"
        
        logger.info(f"🚀 Starting to load embedding model: {self.model_name}")
        logger.info(f"   Device: {self.device}")
        logger.info(f"   Path type: {'Local path' if os.path.exists(self.model_name) else 'Model name'}")
        
        try:
            if USE_FLAG_EMBEDDING and ('bge-m3' in self.model_name.lower() or os.path.exists(self.model_name)):
                # Use FlagEmbedding to load BGE-M3
                logger.info("   Using FlagEmbedding (BGE-M3)")
                self.model_type = 'm3'
                
                # Enable FP16 acceleration in CUDA environment
                use_fp16 = True if self.device == 'cuda' else False
                if use_fp16:
                    logger.info("   ✅ FP16 half-precision acceleration enabled (CUDA)")
                else:
                    logger.info("   ℹ️  Using FP32 precision (CPU)")
                
                # If path exists, use local path directly; otherwise use model name
                if os.path.exists(self.model_name):
                    logger.info(f"   📂 Using local model path")
                else:
                    logger.info(f"   🌐 Using model name")
                
                self.model = BGEM3FlagModel(
                    self.model_name,
                    use_fp16=use_fp16
                )
            elif USE_SENTENCE_TRANSFORMER:
                # Use SentenceTransformer to load other BGE models
                logger.info("   Using SentenceTransformer")
                self.model_type = 'st'
                self.model = SentenceTransformer(self.model_name, device=self.device)
            else:
                raise ImportError("FlagEmbedding or SentenceTransformer not installed, please run: pip install FlagEmbedding sentence-transformers")
            
            logger.info(f"✅ Model loaded successfully!")
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            raise

    def encode(self, texts: List[str], batch_size: int = 32) -> dict:
        """
        Unified encoding interface (compatible with different calling methods)
        
        Args:
            texts: Text list
            batch_size: Batch size
            
        Returns:
            Dictionary containing 'dense_vecs', format consistent with FlagEmbedding
        """
        if self.model_type == 'm3':
            embedding_result = self.model.encode(
                texts,
                batch_size=batch_size,
                max_length=512
            )
            # Return FlagEmbedding result format directly
            return embedding_result
        else:
            # SentenceTransformer format conversion
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=False,
                batch_size=batch_size,
                show_progress_bar=False
            )
            
            # Convert to FlagEmbedding format
            return {'dense_vecs': embeddings}

    def encode_news(self, headline: str, summary: str = "", url: str = "") -> List[float]:
        """
        Generate semantic vector for news

        Args:
            headline: News headline
            summary: News summary
            url: News URL

        Returns:
            Normalized vector (1024 dimensions)
        """
        content_parts = [headline]
        if summary:
            content_parts.append(summary)

        content = " ".join(content_parts)

        if self.model_type == 'm3':
            embedding_result = self.model.encode(
                [content],
                batch_size=1,
                max_length=512
            )
            embedding = embedding_result['dense_vecs'][0]
        else:
            embedding = self.model.encode(
                content,
                normalize_embeddings=False,
                show_progress_bar=False
            )
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.tolist()

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Batch generate vectors

        Args:
            texts: Text list
            batch_size: Batch size

        Returns:
            Vector list
        """
        if self.model_type == 'm3':
            embedding_result = self.model.encode(
                texts,
                batch_size=batch_size,
                max_length=512
            )
            embeddings = embedding_result['dense_vecs']
        else:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=False,
                batch_size=batch_size,
                show_progress_bar=True
            )
        
        # Normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        embeddings_normalized = embeddings / norms

        return embeddings_normalized.tolist()

    def encode_texts(self, headlines: List[str], summaries: List[str] = None) -> List[List[float]]:
        """
        Encode news list

        Args:
            headlines: Headline list
            summaries: Summary list (optional)

        Returns:
            Vector list
        """
        if summaries is None:
            summaries = [""] * len(headlines)

        texts = [
            f"{headline} {summary}"
            for headline, summary in zip(headlines, summaries)
        ]

        return self.encode_batch(texts)