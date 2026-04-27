"""
LLM-Enhanced Intent Recognizer - Using Large Language Models to Understand User Intent
"""
import logging
import json
import importlib
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
import sys
import os

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Intent type enumeration - Only supports three core functions"""
    COMPANY_ANALYSIS = "company_analysis"  # Company analysis
    INDUSTRY_ANALYSIS = "industry_analysis"  # Industry analysis
    NEWS_QUERY = "news_query"  # News query
    UNKNOWN = "unknown"  # Unknown intent (triggers fallback message)


@dataclass
class ExtractedEntity:
    """Extracted entity"""
    entity_type: str  # Entity type (ticker/company/industry/time)
    value: str  # Entity value
    confidence: float = 1.0  # Confidence score


@dataclass
class IntentResult:
    """Intent recognition result"""
    intent_type: IntentType  # Intent type
    confidence: float  # Confidence (0-1)
    entities: List[ExtractedEntity] = field(default_factory=list)  # Extracted entities
    parameters: Dict[str, any] = field(default_factory=dict)  # Additional parameters
    raw_query: str = ""  # Original query
    fallback_message: str = ""  # Fallback message (when intent is UNKNOWN)

    def get_tickers(self) -> List[str]:
        """Get all stock tickers"""
        return [e.value for e in self.entities if e.entity_type == 'ticker']

    def get_companies(self) -> List[str]:
        """Get all company names"""
        return [e.value for e in self.entities if e.entity_type == 'company']

    def get_industries(self) -> List[str]:
        """Get all industry names"""
        return [e.value for e in self.entities if e.entity_type == 'industry']

    def get_time_range(self) -> Optional[str]:
        """Get time range"""
        time_entities = [e for e in self.entities if e.entity_type == 'time']
        return time_entities[0].value if time_entities else None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
            "entities": [
                {"type": e.entity_type, "value": e.value, "confidence": e.confidence}
                for e in self.entities
            ],
            "parameters": self.parameters,
            "raw_query": self.raw_query,
            "fallback_message": self.fallback_message
        }


class LLMIntentRecognizer:
    """
    LLM-enhanced intent recognizer
    - Uses LLM to understand user natural language
    - Accurately identifies three core function intents
    - Automatically extracts key entities
    - Returns fallback message for unsupported functions
    """

    def __init__(self, llm_client=None):
        """
        Initialize intent recognizer
        
        Args:
            llm_client: LLM client instance (optional, lazy loading if not provided)
        """
        self.llm_client = llm_client
        self._llm_initialized = False
        self.prompt_template = None
        
        # Load YAML Prompt template
        self._load_prompt_template()
        
        logger.info("✅ LLM Intent recognizer initialized successfully")

    def _load_prompt_template(self):
        """Load YAML Prompt template"""
        try:
            _prompt_loader_module = importlib.import_module('09_retrieve.prompt_loader')
            PromptLoader = _prompt_loader_module.PromptLoader

            # Use prompts subdirectory of current file's directory
            prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')

            loader = PromptLoader(prompts_dir=prompts_dir)
            template_data = loader.load_template('intent_recognition')

            # Extract required fields
            self.prompt_template = {
                'system_prompt': template_data.get('system_prompt', ''),
                'user_template': template_data.get('user_template', 'User input: {query}'),
                'fallback_message': template_data.get('fallback_message', ''),
                'supported_industries': template_data.get('supported_industries', [])
            }

            logger.info(f"✅ Successfully loaded Intent recognition Prompt template")
        except Exception as e:
            logger.error(f"❌ Failed to load Prompt template: {e}, using default template")
            self._use_default_template()

    def _use_default_template(self):
        """Use default template (fallback solution)"""
        self.prompt_template = {
            'system_prompt': """You are a professional financial analysis assistant intent recognition expert. Your task is to accurately understand user intent and extract key information.

# Supported Functions (Only the following three categories)

## 1. Company Analysis (company_analysis)
- Analyze specific company fundamentals, financial performance, risk assessment
- Examples: "Analyze Apple", "How is AAPL"

## 2. Industry Analysis (industry_analysis)
- Analyze industry trends, competitive landscape, supply chain
- Supported industries: Technology, Finance, Healthcare, Consumer Retail, Energy, Automotive Manufacturing, Real Estate, Telecommunications
- Examples: "Technology industry outlook", "Analyze finance industry"

## 3. News Query (news_query)
- Query latest news for specific companies
- Examples: "Latest news about Apple", "AAPL recent updates"

# Recognition Rules
1. If user asks about a specific company → company_analysis
2. If user asks about an industry → industry_analysis  
3. If user asks about news/updates/information → news_query
4. If user's question doesn't belong to above three categories → unknown

# Output Format
You must output in JSON format, do not add additional explanations""",
            'user_template': 'User input: {query}',
            'fallback_message': "Hello! It seems your question is beyond my capabilities 🤔\n\nLet me introduce what I can do:\n\n**If you want to analyze a company**\n   Say: \"Analyze [company name]\" or \"How is [stock ticker]\"\n   Example: \"Analyze Apple Inc.\" / \"How is AAPL performing\"\n\n**If you want to understand an industry**\n   Say: \"[Industry name] industry analysis\"\n   Example: \"How is the technology industry outlook\" / \"Finance industry analysis\"\n\n**If you want to see latest news**\n   Say: \"Latest news about [company name]\"\n   Example: \"Recent news about Tesla\" / \"BABA today's updates\"\n\nCurrently supported industries include:\nTechnology, Finance, Healthcare, Consumer Retail, Energy, Automotive Manufacturing, Real Estate, Telecommunications, etc.\n\nWhat would you like to know? 😊",
            'supported_industries': []
        }

    def initialize_llm(self, use_cloud: bool = None, device: str = None):
        """
        Initialize LLM client

        Args:
            use_cloud: Whether to use cloud LLM
            device: Computing device
        """
        if self._llm_initialized:
            return

        try:
            # Get default model from configuration
            _config_module = importlib.import_module('05_config.settings')
            Config = _config_module.Config
            model_name = Config.DEFAULT_LLM_MODEL

            # Initialize RAG service to get LLM client
            _rag_module = importlib.import_module('09_retrieve.rag_service')
            RAGService = _rag_module.RAGService

            rag = RAGService(device=device)
            rag.initialize_llm(model=model_name, use_cloud=use_cloud)
            self.llm_client = rag.llm_client
            self._llm_initialized = True

            logger.info(f"✅ LLM client initialized successfully: {model_name}")
        except Exception as e:
            logger.error(f"❌ LLM client initialization failed: {e}")
            raise

    def recognize(self, query: str) -> IntentResult:
        """
        Recognize user intent

        Args:
            query: User query text

        Returns:
            Intent recognition result
        """
        logger.info(f"🔍 LLM recognizing intent: {query}")

        # Ensure LLM is initialized
        if not self._llm_initialized or not self.llm_client:
            self.initialize_llm()

        try:
            # Build system prompt
            system_prompt = self.prompt_template.get('system_prompt', '')

            # Build user message
            user_template = self.prompt_template.get('user_template', 'User input: {query}')
            user_message = user_template.format(query=query)

            # Call LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            response = self.llm_client.chat(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )

            # Parse LLM response
            intent_result = self._parse_llm_response(response, query)
            
            # Validate entity completeness and generate hints
            needs_hint, hint_message = self._validate_and_generate_hint(intent_result)
            if needs_hint:
                intent_result.fallback_message = hint_message
                intent_result.confidence = 0.5  # Lower confidence to indicate clarification needed
            
            logger.info(f"   Intent: {intent_result.intent_type.value}, Confidence: {intent_result.confidence:.2f}")
            logger.info(f"   Entities: {len(intent_result.entities)} items")
            if intent_result.get_tickers():
                logger.info(f"   Stock Tickers: {', '.join(intent_result.get_tickers())}")
            if intent_result.get_companies():
                logger.info(f"   Company Names: {', '.join(intent_result.get_companies())}")
            
            return intent_result

        except Exception as e:
            logger.error(f"❌ LLM Intent recognition failed: {e}, falling back to rule-based recognition")
            return self._fallback_rule_based_recognition(query)

    def _parse_llm_response(self, response: str, raw_query: str) -> IntentResult:
        """Parse LLM response"""
        try:
            # Clean and extract JSON
            json_str = response.strip()

            # Option 1: Try to extract ``json ... ```  code block
            if '```json' in response:
                parts = response.split('```json')
                if len(parts) > 1:
                    json_str = parts[1].split('```')[0].strip()
            # Option 2: Try to extract ``` ... ```  code block (no language tag)
            elif '```' in response:
                parts = response.split('```')
                if len(parts) >= 3:  # Ensure there is a code block
                    json_str = parts[1].strip()  # Take the first code block content

            # Option 3: If response is directly JSON, parse it
            # (If above already extracted a code block, this won't execute)

            # Parse JSON
            parsed = json.loads(json_str)

            # Parse intent type (fix case issues)
            intent_type_str = parsed.get('intent_type', 'unknown')
            intent_type = IntentType.UNKNOWN

            # Exact match intent type
            for enum_member in IntentType:
                if enum_member.value == intent_type_str:
                    intent_type = enum_member
                    break

            try:
                # Try to match enum value
                for enum_member in IntentType:
                    if enum_member.value == intent_type_str:
                        intent_type = enum_member
                        break
            except (ValueError, AttributeError):
                intent_type = IntentType.UNKNOWN

            # Parse confidence (add range limits)
            confidence = float(parsed.get('confidence', 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Limit to 0-1

            # Parse entities
            entities = []
            for entity_data in parsed.get('entities', []):
                try:
                    entities.append(ExtractedEntity(
                        entity_type=entity_data.get('entity_type', 'unknown'),
                        value=entity_data.get('value', ''),
                        confidence=max(0.0, min(1.0, float(entity_data.get('confidence', 0.8))))
                    ))
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Failed to parse entity: {e}, data: {entity_data}")
                    continue

            # Parse parameters
            parameters = parsed.get('parameters', {})

            # If unknown intent, set fallback message
            fallback_message = ""
            if intent_type == IntentType.UNKNOWN:
                fallback_message = self.prompt_template.get('fallback_message', '')

            return IntentResult(
                intent_type=intent_type,
                confidence=confidence,
                entities=entities,
                parameters=parameters,
                raw_query=raw_query,
                fallback_message=fallback_message
            )

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}, response content: {response[:200]}...")
            fallback_message = self.prompt_template.get('fallback_message', '')
            return IntentResult(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                entities=[],
                parameters={},
                raw_query=raw_query,
                fallback_message=fallback_message
            )
        except Exception as e:
            logger.error(f"❌ Failed to parse LLM response: {e}")
            logger.error(f"Response content: {response[:500]}")
            fallback_message = self.prompt_template.get('fallback_message', '')
            return IntentResult(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                raw_query=raw_query,
                fallback_message=fallback_message
            )

    def _validate_and_generate_hint(self, intent_result: IntentResult) -> tuple:
        """
        Validate entity completeness and generate hint information
        
        Args:
            intent_result: Intent recognition result
            
        Returns:
            (whether hint is needed, hint message)
        """
        intent_type = intent_result.intent_type
        
        # Company analysis needs company name or stock ticker
        if intent_type.name == 'COMPANY_ANALYSIS':
            if not intent_result.get_companies() and not intent_result.get_tickers():
                return True, "Please specify the company name or stock ticker to analyze, e.g., 'Analyze Apple' or 'AAPL how is it'"
        
        # Industry analysis needs industry name
        elif intent_type.name == 'INDUSTRY_ANALYSIS':
            if not intent_result.get_industries():
                return True, "Please specify the industry to analyze, e.g., 'Technology industry outlook' or 'Finance industry analysis'\n\nSupported industries: Technology, Finance, Healthcare, Consumer Retail, Energy, Automotive Manufacturing, Real Estate, Telecommunications"
        
        # News query needs company name or stock ticker
        elif intent_type.name == 'NEWS_QUERY':
            if not intent_result.get_companies() and not intent_result.get_tickers():
                return True, "Please specify the company to query news for, e.g., 'Latest news about Apple' or 'AAPL recent updates'"
        
        return False, ""

# Convenience function
def recognize_intent(query: str, llm_client=None) -> IntentResult:
    """
    Quickly recognize intent

    Args:
        query: User query
        llm_client: LLM client (optional)

    Returns:
        Intent recognition result
    """
    recognizer = LLMIntentRecognizer(llm_client=llm_client)
    return recognizer.recognize(query)
