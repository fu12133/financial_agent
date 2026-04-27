"""
LLM Client - Unified interface supporting cloud (Qwen) and local (Transformers) models
"""
import sys
import os
import logging
import json
from typing import Dict, Optional, List
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class UnifiedLLMClient:
    """Unified LLM client supporting cloud and local models"""

    def __init__(self, model: str = None, use_cloud: bool = None,
                 device: str = None, use_quantization: bool = None,
                 api_key: str = None):
        """
        Initialize unified LLM client

        Args:
            model: Model name
                   - Cloud: qwen-plus, qwen-turbo, qwen-max, qwen-long, qwen2.5-*, qwen3-*, etc.
                   - Local: Qwen/Qwen2.5-7B-Instruct or local path
            use_cloud: Whether to use cloud (True=cloud, False=local, None=auto-detect)
            device: Computing device ('cuda' or 'cpu', local mode only)
            use_quantization: Whether to use 4bit quantization (local mode only, default True)
            api_key: API Key (cloud mode only)
        """
        # Read configuration from environment variables
        self.model = model or os.getenv("DEFAULT_LLM_MODEL", "qwen-plus")

        # Auto-detect whether to use cloud
        if use_cloud is None:
            # Extended cloud model recognition rules
            cloud_models = ['qwen-plus', 'qwen-turbo', 'qwen-max', 'qwen-long']
            # Check if it's a standard cloud model
            is_standard_cloud = any(cloud in self.model.lower() for cloud in cloud_models)
            # Check if it's qwen2.5/qwen3 cloud versions (but without slash, slash usually indicates local HuggingFace model)
            is_qwen_cloud_version = ('qwen2.5' in self.model.lower() or 'qwen3' in self.model.lower()) and '/' not in self.model
            
            self.use_cloud = is_standard_cloud or is_qwen_cloud_version
        else:
            self.use_cloud = use_cloud

        # Read LLM parameters from environment variables
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))

        if self.use_cloud:
            # Cloud mode configuration
            self.max_tokens = int(os.getenv("CLOUD_LLM_MAX_TOKENS", "8192"))
            self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")

            if not self.api_key:
                raise ValueError("Cloud mode requires DASHSCOPE_API_KEY to be set")

            self._init_cloud_client()
        else:
            # Local mode configuration
            self.max_tokens = int(os.getenv("LOCAL_LLM_MAX_TOKENS", os.getenv("HF_MAX_NEW_TOKENS", "4096")))
            self.device = device or ('cuda' if self._is_cuda_available() else 'cpu')
            self.use_quantization = use_quantization if use_quantization is not None else True

            self._init_local_client()

        logger.info(f"✅ LLM client initialized successfully")
        logger.info(f"   Mode: {'Cloud' if self.use_cloud else 'Local'}")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Temperature: {self.temperature}")
        logger.info(f"   Max tokens: {self.max_tokens}")

    def _is_cuda_available(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def _init_cloud_client(self):
        """Initialize cloud client"""
        try:
            import dashscope
            from dashscope import Generation

            dashscope.api_key = self.api_key

            # Test connection
            response = Generation.call(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )

            if response.status_code == 200:
                logger.info(f"✅ Cloud model '{self.model}' ready")
            else:
                logger.warning(f"⚠️  Cloud model '{self.model}' may not be available: {response.message}")

            self.cloud_generation = Generation

        except ImportError:
            raise ImportError("Please install dashscope: pip install dashscope")
        except Exception as e:
            logger.error(f"❌ Cloud client initialization failed: {e}")
            raise

    def _init_local_client(self):
        """Initialize local client"""
        try:
            import torch
            import glob
            from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig

            # If path points to snapshots directory, automatically find specific snapshot
            if os.path.isdir(self.model) and 'snapshots' in self.model:
                snapshot_dirs = glob.glob(os.path.join(self.model, '*'))
                if snapshot_dirs:
                    self.model = snapshot_dirs[0]
                    logger.info(f"📂 Found local snapshot: {self.model}")
                else:
                    logger.warning(f"⚠️  No snapshot directory found")

            logger.info(f"📥 Loading local model: {self.model}")
            logger.info(f"   Device: {self.device}")
            logger.info(f"   Quantization: {'4bit' if self.use_quantization else 'FP16'}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model,
                trust_remote_code=True,
                local_files_only=True  # Only use local files, don't attempt download
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model
            model_kwargs = {
                "device_map": "auto" if self.device == "cuda" else None,
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
                "local_files_only": True  # Only use local files
            }

            if self.use_quantization and self.device == "cuda":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["torch_dtype"] = torch.float16
            else:
                model_kwargs["torch_dtype"] = torch.float16 if self.device == "cuda" else torch.float32

            if self.device == "cpu":
                model_kwargs.pop("device_map")

            self.model_instance = AutoModelForCausalLM.from_pretrained(
                self.model,
                **model_kwargs
            )

            if self.device == "cpu":
                self.model_instance = self.model_instance.to(self.device)

            self.model_instance.eval()
            self.GenerationConfig = GenerationConfig

            # Display model information
            if self.device == "cuda":
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                logger.info(f"✅ Local model loaded successfully")
                logger.info(f"   GPU: {gpu_name}")
                logger.info(f"   Total VRAM: {gpu_memory:.1f} GB")
                logger.info(f"   Allocated: {allocated:.1f} GB")
            else:
                logger.info(f"✅ Local model loaded successfully (CPU mode)")

            num_params = sum(p.numel() for p in self.model_instance.parameters()) / 1e9
            logger.info(f"   Model parameters: {num_params:.2f}B")

        except ImportError:
            raise ImportError("Please install transformers: pip install transformers accelerate bitsandbytes")
        except Exception as e:
            logger.error(f"❌ Local client initialization failed: {e}")
            raise

    def check_model_availability(self) -> bool:
        """Check if model is available"""
        if self.use_cloud:
            try:
                response = self.cloud_generation.call(
                    model=self.model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                return response.status_code == 200
            except Exception as e:
                logger.error(f"❌ Failed to check cloud model: {e}")
                return False
        else:
            # Local model already loaded during initialization
            return True

    def generate_impact_analysis(self, prompt: str,
                                temperature: float = None,
                                max_tokens: int = None) -> Dict:
        """
        Generate impact analysis result

        Args:
            prompt: Impact Analysis Prompt
            temperature: Temperature parameter (0-1), defaults from .env
            max_tokens: Maximum generation length, defaults from .env

        Returns:
            Raw response content
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        mode = "Cloud" if self.use_cloud else "Local"
        logger.info(f"🤖 Calling {mode} LLM: {self.model}")
        logger.info(f"   Prompt length: {len(prompt)} characters")
        logger.info(f"   Temperature: {temp}, Max tokens: {tokens}")

        if self.use_cloud:
            return self._cloud_generate(prompt, temp, tokens)
        else:
            return self._local_generate(prompt, temp, tokens)

    def _cloud_generate(self, prompt: str, temperature: float, max_tokens: int) -> Dict:
        """Cloud generation"""
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Retrying cloud LLM call (attempt {attempt + 1}/{max_retries})...")
                else:
                    logger.info(f"📤 Calling cloud LLM: {self.model}")

                response = self.cloud_generation.call(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional financial analyst. Please conduct 5-dimensional impact analysis. Output JSON format result directly, do not output thinking process, explanations, or any extra text. Only output pure JSON object, do not use code blocks. Strictly follow JSON format, do not add any extra text."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    enable_thinking=False
                )

                if response.status_code != 200:
                    error_msg = f"API call failed: {response.code} - {response.message}"
                    logger.error(f"❌ {error_msg}")
                    return {"error": error_msg, "model": self.model}

                content = response.output.text.strip()

                if not content:
                    logger.error("❌ LLM returned empty content")
                    return {"error": "LLM returned empty response", "model": self.model}

                logger.info(f"✅ Cloud LLM response successful ({len(content)} characters)")

                return {"raw_response": content, "model": self.model}

            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ LLM call failed (attempt {attempt + 1}/{max_retries}): {last_error}")

                # If connection issue, wait and retry
                if "Connection" in last_error or "timeout" in last_error.lower():
                    import time
                    wait_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                    logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    # Non-connection issue, return directly
                    break

        # All retries failed
        logger.error(f"❌ LLM call ultimately failed after {max_retries} retries")
        
        error_msg = last_error or "Unknown error"
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            logger.warning("⚠️  API Key authentication failed")
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            logger.warning("⚠️  May have exceeded quota limit")
        elif "timeout" in error_msg.lower() or "Connection" in error_msg:
            logger.warning("⚠️  Network connection issue, please check network connection")

        return {"error": error_msg, "model": self.model}

    def _local_generate(self, prompt: str, temperature: float, max_tokens: int) -> Dict:
        """Local generation"""
        try:
            import torch

            system_prompt = """You are a professional financial analyst. Please conduct 5-dimensional impact analysis. Directly output JSON format result, prohibit outputting any thinking, reasoning, analysis process, notes, explanatory text; prohibit redundant line breaks, extra descriptions, opening remarks, closing remarks; strictly follow specified JSON structure and field requirements, do not modify format or add supplements; all analysis based only on given news and background facts, objectively output final content."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            inputs = self.tokenizer(text, return_tensors="pt").to(self.model_instance.device)
            input_length = inputs.input_ids.shape[1]

            logger.info(f"📤 Generating local LLM response...")

            generation_config = self.GenerationConfig(
                temperature=temperature,
                max_new_tokens=max_tokens,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.05,
                top_p=0.95,
                top_k=40
            )

            with torch.no_grad():
                outputs = self.model_instance.generate(
                    **inputs,
                    generation_config=generation_config
                )

            generated_tokens = outputs[0][input_length:]
            content = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

            if not content or not content.strip():
                logger.error("❌ LLM returned empty content")
                return {"error": "LLM returned empty response", "model": self.model}

            logger.info(f"✅ Local LLM response successful ({len(content)} characters)")

            return {"raw_response": content.strip(), "model": self.model}

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ LLM call failed: {error_msg}")

            if "out of memory" in error_msg.lower() or "cuda" in error_msg.lower():
                logger.warning("⚠️  Insufficient VRAM")
                logger.warning("💡 Suggestion: Use smaller model, reduce max_tokens, use CPU mode, or enable quantization")
            elif "not found" in error_msg.lower():
                logger.warning(f"⚠️  Model '{self.model}' not found")

            return {"error": error_msg, "model": self.model}

    def chat(self, messages: list, temperature: float = None, max_tokens: int = None) -> str:
        """
        General chat interface

        Args:
            messages: Message list, format [{"role": "user", "content": "..."}]
            temperature: Temperature parameter, defaults from .env
            max_tokens: Maximum generation length, defaults from .env

        Returns:
            Response text
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        if self.use_cloud:
            try:
                response = self.cloud_generation.call(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=tokens,
                    enable_thinking=False
                )

                if response.status_code == 200:
                    return response.output.text
                else:
                    error_msg = f"API call failed: {response.code} - {response.message}"
                    logger.error(f"❌ Chat failed: {error_msg}")
                    return f"Error: {error_msg}"
            except Exception as e:
                logger.error(f"❌ Chat failed: {e}")
                return f"Error: {e}"
        else:
            try:
                import torch

                text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )

                inputs = self.tokenizer(text, return_tensors="pt").to(self.model_instance.device)
                input_length = inputs.input_ids.shape[1]

                generation_config = self.GenerationConfig(
                    temperature=temp,
                    max_new_tokens=tokens,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )

                with torch.no_grad():
                    outputs = self.model_instance.generate(
                        **inputs,
                        generation_config=generation_config
                    )

                generated_tokens = outputs[0][input_length:]
                return self.tokenizer.decode(generated_tokens, skip_special_tokens=True)

            except Exception as e:
                logger.error(f"❌ Chat failed: {e}")
                return f"Error: {e}"


def create_llm_client(model: str = None, use_cloud: bool = None,
                     device: str = None, use_quantization: bool = None,
                     api_key: str = None) -> UnifiedLLMClient:
    """Create unified LLM client

    Args:
        model: Model name
        use_cloud: Whether to use cloud (None=auto-detect)
        device: Computing device (local mode only)
        use_quantization: Whether to use quantization (local mode only)
        api_key: API Key (cloud mode only)

    Returns:
        UnifiedLLMClient instance
    """
    return UnifiedLLMClient(
        model=model,
        use_cloud=use_cloud,
        device=device,
        use_quantization=use_quantization,
        api_key=api_key
    )
