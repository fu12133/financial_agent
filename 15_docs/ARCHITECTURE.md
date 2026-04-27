# Financial Agent Architecture Documentation

## Overview
The Financial Agent is an intelligent financial analysis system that combines Retrieval-Augmented Generation (RAG), multi-layer news classification, memory management, and LLM-powered analysis to provide comprehensive company and industry insights. The system processes financial news in real-time, stores them in a vector database, and generates detailed analytical reports with quality evaluation.

---

## Table of Contents
- #system-architecture
- #module-structure
- #core-components
  - #api-layer-01_backend
  - #frontend-02_frontend
  - #agent-core-03_agent
  - #financial-data-apis-04_api
  - #configuration-05_config
  - #intent-recognition-06_intent
  - #memory-system-07_memory
  - #news-processing-pipeline-08_pipeline
  - #rag--retrieval-09_retrieve
  - #storage-10_storage
  - #report-generation-11_report
  - #utilities-12_utils
- #data-flow
- #technology-stack
- #deployment-architecture
- #design-patterns
- #key-features
- #performance-considerations
- #security-considerations
- #monitoring--observability
- #future-enhancements
- #troubleshooting
- #contributing
- #glossary
- #references
- #license
- #contact

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        System Architecture                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────┐     ┌─────────────┐     ┌─────────────────────┐    │
│  │   User     │────▶│  Frontend   │────▶│   FastAPI Backend   │    │
│  └────────────┘     │  (React)    │     │   (01_backend)      │    │
│                     └─────────────┘     └──────────┬──────────┘    │
│                                                     │               │
│  ┌──────────────────────────────────────────────────┼─────────────┐ │
│  │                  Agent Core (03_agent)          │               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┴──────────┐    │ │
│  │  │   Intent    │  │   Memory    │  │       RAG           │    │ │
│  │  │ Recognition │  │   System    │  │     Service         │    │ │
│  │  │ (06_intent) │  │ (07_memory) │  │  (09_retrieve)      │    │ │
│  │  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘    │ │
│  │         │                │                    │               │ │
│  │  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────────┴──────────┐    │ │
│  │  │   LLM       │  │   Milvus    │  │    LLM Client       │    │ │
│  │  │  Intent     │  │   Vector    │  │  (Cloud/Local)      │    │ │
│  │  │ Recognizer  │  │    DB       │  └──────────┬──────────┘    │ │
│  │  └─────────────┘  └─────────────┘             │               │ │
│  │                                                │               │ │
│  │  ┌─────────────────────────────────────────────┼─────────────┐ │ │
│  │  │             News Processing Pipeline        │             │ │ │
│  │  │              (08_pipeline)                  │             │ │ │
│  │  │  ┌─────────┐ ┌─────────┐ ┌──────────────┐  │             │ │ │
│  │  │  │  News   │ │  BGE-M3 │ │  4-Layer     │  │             │ │ │
│  │  │  │Collector│▶│Embedding│▶│ Classifier   │──┘             │ │ │
│  │  │  └─────────┘ └─────────┘ └──────────────┘                │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                                                                │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │            External Data Sources (04_API)                │  │ │
│  │  │                     ┌────────────┐                       │  │ │
│  │  │                     │  Finnhub   │───────────────────────┘  │ │
│  │  │                     │    API     │                          │ │
│  │  │                     └────────────┘                          │ │
│  │  └──────────────────────────────────────────────────────────────┘ │
│  └────────────────────────────────────────────────────────────────────┘
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐
│  │                  Report Generation (11_report)                     │ │
│  │              ┌──────────────────────────────┐                     │ │
│  │              │    Company/Industry         │                     │ │
│  │              │     Analysis Reports        │                     │ │
│  │              └──────────────────────────────┘                     │ │
│  └─────────────────────────────────────────────────────────────────────┘
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Module Structure

### Directory Layout
```
financial_agent_V1/
├── 01_backend/              # FastAPI Backend Service
│   ├── api/                 # API Routes
│   ├── core/                # Configuration & Settings
│   ├── models/              # Pydantic Schemas
│   ├── services/            # Business Logic Services
│   └── main.py              # Application Entry Point
│
├── 02_frontend/             # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/      # Reusable UI Components
│   │   ├── pages/           # Page Components
│   │   ├── services/        # API Client
│   │   └── types/           # TypeScript Types
│   └── vite.config.ts       # Vite Configuration
│
├── 03_agent/                # Agent Core
│   └── agent_core.py        # FinancialAgent Implementation
│
├── 04_API/                  # External API Clients
│   ├── finnhub/             # Finnhub API SDK
│   └── finnhub_client.py    # Finnhub Client Wrapper
│
├── 05_config/               # Configuration Management
│   └── settings.py          # Centralized Settings
│
├── 06_intent/               # Intent Recognition
│   ├── prompts/             # Intent Recognition Prompts
│   ├── intent_recognizer.py # Rule-based Intent Recognition
│   ├── llm_intent_recognizer.py  # LLM-based Intent Recognition
│   └── intent_processor.py  # Intent Routing & Processing
│
├── 07_memory/               # Memory Management System
│   ├── memory_manager.py    # Unified Memory Manager
│   ├── short_term_memory.py # Session-based Memory
│   ├── long_term_memory.py  # Persistent Memory (Milvus)
│   └── memory_types.py      # Memory Type Definitions
│
├── 08_pipeline/             # News Processing Pipeline
│   ├── embedding.py         # BGE-M3 Embedding Engine
│   ├── classifier.py        # 4-Layer News Classifier
│   └── news_processor.py    # Pipeline Orchestrator
│
├── 09_retrieve/             # RAG & Retrieval System
│   ├── prompts/             # Analysis Prompt Templates
│   ├── rag_service.py       # RAG Service Interface
│   ├── rag_searcher.py      # Hybrid Search (Vector + BM25)
│   ├── llm_client.py        # Unified LLM Client (Cloud/Local)
│   ├── evaluation.py        # Quality Evaluation Engine
│   ├── json_convertor.py    # LLM Response Parser
│   └── prompt_loader.py     # YAML Prompt Template Loader
│
├── 10_storage/              # Storage Layer
│   ├── milvus_manager.py    # Milvus Vector DB Operations
│   └── news_collector_service.py  # News Collection Service
│
├── 11_report/               # Report Generation
│   └── report_generator.py  # Company/Industry Report Generator
│
├── 12_utils/                # Utility Functions
│   └── logging_config.py    # Logging Configuration
│
├── 13_tests/                # Test Suite
│   └── test_*.py            # Unit & Integration Tests
│
├── 14_scripts/              # Operational Scripts
│   ├── collect_news.py      # News Collection Script
│   ├── quick_collect.py     # Quick News Collection
│   ├── recreate_long_term_memory.py  # Memory Rebuild Script
│   └── scheduler.py         # Scheduled Task Runner
│
└── 15_docs/                 # Documentation
    ├── API.md               # API Documentation
    ├── ARCHITECTURE.md      # Architecture Documentation
    └── README.md            # Project Overview
```

---

## Core Components

### API Layer (01_backend)
**Purpose:** RESTful API service built with FastAPI

**Key Files:**
- `main.py` - FastAPI application entry point with CORS middleware
- `api/routes.py` - API endpoint definitions
- `models/schemas.py` - Pydantic request/response models
- `services/agent_service.py` - Agent orchestration service
- `services/news_service.py` - News query service
- `core/config.py` - Environment-based configuration

**Endpoints:**
- `GET /health` - Health check
- `GET /` - API information
- `POST /api/v1/chat` - Chat with intent recognition
- `POST /api/v1/analyze/company` - Company analysis
- `POST /api/v1/analyze/industry` - Industry analysis
- `POST /api/v1/news/query` - News retrieval
- `POST /api/v1/watchlist` - Watchlist management
- `GET /api/v1/watchlist/{user_id}` - Get user watchlist

**Architecture Pattern:** Service-Oriented Architecture (SOA)

---

### Frontend (02_frontend)
**Purpose:** Modern React-based user interface

**Technology Stack:**
- React 18 with TypeScript
- Ant Design 5 for UI components
- Vite for build tooling
- React Router 6 for navigation
- Axios for HTTP requests

**Key Pages:**
- **Home** - Landing page with feature overview
- **Company Analysis** - Detailed company analysis view
- **Industry Analysis** - Industry trend analysis view
- **Chat** - Conversational interface

**Key Components:**
- **DimensionCard** - Displays analysis dimensions with scores
- **StorylineView** - Event timeline visualization
- **QualityReport** - Quality evaluation display
- **NewsList** - News article listing
- **Layout** - Main application layout

**Proxy Configuration:**
```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

---

### Agent Core (03_agent)
**Purpose:** Central orchestrator for all agent operations

**Class:** `FinancialAgent`

**Key Responsibilities:**
1. **Session Management** - Maintain conversation context
2. **Intent Handling** - Route requests based on recognized intent
3. **Model Selection** - Auto-detect cloud vs local LLM
4. **Memory Integration** - Save/retrieve from memory system
5. **Analysis Execution** - Trigger company/industry analysis

**Agent States:**
```python
class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"
```

**Agent Modes:**
```python
class AgentMode(Enum):
    CHAT = "chat"
    ANALYSIS = "analysis"
    REPORT = "report"
```

**Main Methods:**
- `chat(message)` - Process natural language queries
- `analyze_company(ticker, days)` - Perform company analysis
- `analyze_industry(industry, days)` - Perform industry analysis
- `query_news(ticker, days, limit)` - Retrieve news articles
- `start_session()` / `end_session()` - Manage conversation sessions

**Lazy Initialization Pattern:**
Components are initialized on-demand to avoid circular imports and reduce startup time.

---

### Financial Data APIs (04_API)
**Purpose:** External data source integration

**Finnhub Integration:**
- Real-time stock market data
- Company fundamentals
- Market news feed
- Auto-generated SDK from OpenAPI spec

**Validator Module:**
- Input validation for tickers and symbols
- Data format verification
- Error handling for API failures

---

### Configuration (05_config)
**Purpose:** Centralized configuration management

**Settings Class:**
```python
class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database
    DB_HOST: str
    DB_PORT: int
    MILVUS_URI: str = "http://localhost:19530"
    
    # LLM Models
    DEFAULT_LLM_MODEL: str = "qwen-plus"
    QWEN_CLOUD_MODEL: str = "qwen-plus"
    OLLAMA_MODEL: str = "qwen3.5:9b"
    
    # API Keys
    FINNHUB_API_KEY: str
    DASHSCOPE_API_KEY: str
    
    # Analysis Parameters
    ANALYSIS_DAYS: int = 7
    LLM_TEMPERATURE: float = 0.7
    RAG_TOP_K: int = 30
```

**Environment Variables:** Loaded from `.env` file using Pydantic Settings

---

### Intent Recognition (06_intent)
**Purpose:** Understand user intent from natural language queries

**Architecture:**
```
User Query → IntentRecognizer → IntentResult → IntentProcessor → Action
```

**Intent Types:**
```python
class IntentType(Enum):
    COMPANY_ANALYSIS = "company_analysis"
    INDUSTRY_ANALYSIS = "industry_analysis"
    NEWS_QUERY = "news_query"
    STOCK_COMPARISON = "stock_comparison"
    MARKET_TREND = "market_trend"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    WATCHLIST_MANAGE = "watchlist_manage"
    MEMORY_QUERY = "memory_query"
    REPORT_GENERATE = "report_generate"
    GENERAL_CHAT = "general_chat"
```

**Components:**
1. **IntentRecognizer** (Rule-based)
   - Pattern matching with regex
   - Keyword extraction
   - Entity recognition (tickers, companies, industries)
   - Confidence scoring
   - Company-ticker mapping table

2. **LLMIntentRecognizer** (AI-based)
   - Uses LLM for complex intent understanding
   - Handles ambiguous queries
   - Better contextual understanding

3. **IntentProcessor**
   - Routes intents to appropriate handlers
   - Executes actions based on intent type
   - Returns structured responses

**IntentResult Structure:**
```python
{
    "intent_type": IntentType,
    "confidence": float,
    "entities": {
        "tickers": ["AAPL"],
        "companies": ["Apple"],
        "industries": ["technology"],
        "time_range": "7 days"
    },
    "fallback_message": str  # For low confidence
}
```

---

### Memory System (07_memory)
**Purpose:** Maintain context and learn from interactions

**Architecture:**
```
MemoryManager
├── ShortTermMemory (In-memory, session-based)
└── LongTermMemory (Milvus-backed, persistent)
```

**Memory Types:**
```python
class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"

class MemoryCategory(Enum):
    CONVERSATION = "conversation"
    COMPANY_ANALYSIS = "company_analysis"
    USER_PREFERENCE = "user_preference"
    WATCHLIST = "watchlist"
```

**Short-Term Memory:**
- Session-scoped storage
- Fast in-memory access
- Automatic cleanup on session end
- Stores recent conversation history

**Long-Term Memory:**
- Persistent storage in Milvus
- Semantic search capability
- Stores: user preferences, past analyses, watchlist items, important insights
- Importance-based retention (0-1 scale)

**MemoryManager API:**
```python
# Store memory
memory_id = manager.remember(
    content="Analyzed Apple Inc.",
    category=MemoryCategory.COMPANY_ANALYSIS,
    importance=0.8,
    tags=["AAPL", "technology"]
)

# Recall memories
memories = manager.recall(
    query="Apple analysis",
    limit=5,
    use_semantic=True
)

# Get context for LLM
context = manager.get_context(query="tech stocks")
```

**Auto-Decision Logic:**
- Importance > 0.7 → Long-term memory
- Category = USER_PREFERENCE/COMPANY_ANALYSIS/WATCHLIST → Long-term
- Otherwise → Short-term

---

### News Processing Pipeline (08_pipeline)
**Purpose:** Intelligent processing and enrichment of financial news

**Pipeline Stages:**
```
Finnhub API → Validation → Embedding → Deduplication → 
4-Layer Classification → Milvus Ingestion
```

**Components:**
1. **EmbeddingEngine**
   - Model: BGE-M3 (BAAI/bge-m3)
   - Dimensions: 1024
   - Supports both headline and summary encoding
   - Device: CUDA/CPU auto-detection

2. **AdvancedNewsClassifier** (4-Layer Classification)
   
   **Layer 1: Event Type Classification**
   - Product Launch
   - Earnings Report
   - Merger & Acquisition
   - Regulatory Change
   - Executive Change
   - Market Movement
   - Technology Innovation
   - Partnership/Collaboration
   
   **Layer 2: Industry Classification**
   - Technology
   - Finance
   - Healthcare & Pharmaceuticals
   - Consumer Retail
   - Energy & Utilities
   - Automotive & Manufacturing
   - Real Estate
   - Telecommunications
   
   **Layer 3: Sentiment Analysis**
   - Polarity: positive/negative/neutral
   - Intensity: strong/moderate/weak
   - Confidence score (0-1)
   
   **Layer 4: Business Impact Assessment**
   - Primary impact area
   - Multiple business impacts
   - Impact severity

3. **FinancialNewsProcessor**
   - Orchestrates the entire pipeline
   - Batch processing support
   - Duplicate detection via vector similarity
   - Progress tracking and statistics

**Processing Statistics:**
```python
stats = {
    "total_processed": 1000,
    "duplicates_removed": 150,
    "successfully_ingested": 850,
    "errors": 0
}
```

**Duplicate Detection:**
- Cosine similarity threshold: 0.95
- Checks against existing vectors in Milvus
- Prevents redundant storage

---

### RAG & Retrieval (09_retrieve)
**Purpose:** Contextual retrieval and LLM-powered analysis

**Components:**
1. **RAGService** - Main service interface
   - Simple and advanced search
   - Complete retrieval + analysis flow
   - Company and industry analysis methods
   - Quality evaluation integration

2. **RAGSearcher** - Hybrid search engine
   - Vector similarity search (Milvus)
   - BM25 keyword search
   - Hybrid ranking with configurable weights
   - Multi-dimensional filtering

3. **UnifiedLLMClient** - LLM abstraction layer
   - Supports both cloud and local models
   - Cloud: Qwen Plus (DashScope API)
   - Local: Ollama (qwen3.5:9b, etc.)
   - Auto-detection of available models
   - Temperature and token control

4. **ImpactAnalyzer** - Builds analysis prompts
   - Structures retrieved context
   - Formats current news
   - Creates comprehensive prompts

5. **AnalysisEvaluator** - Quality assessment
   - Six evaluation dimensions:
     - Completeness (coverage)
     - Traceability (source citation)
     - Consistency (logical coherence)
     - Depth (insight quality)
     - Timeliness (information recency)
     - Balance (multiple viewpoints)
   - Scoring: 0-100 scale
   - Grade: A/B/C/D/F
   - Issue detection and recommendations

6. **PromptLoader** - YAML-based prompt templates
   - Separates prompts from code
   - Version control friendly
   - Easy customization
   - Templates: `company_analysis.yaml`, `industry_analysis.yaml`

7. **JSONConvertor** - Response parser
   - Extracts JSON from LLM responses
   - Handles malformed output
   - Validates structure
   - Extracts core metrics

**Hybrid Search Algorithm:**
```python
final_score = (vector_weight * vector_score) + (bm25_weight * bm25_score)
# Default weights: vector_weight = 0.7, bm25_weight = 0.3
```

**Company Analysis Flow:**
1. Fetch news from Milvus (ticker + time filter)
2. Sort by recency
3. Select representative news by event type
4. Build prompt using YAML template
5. Call LLM for analysis
6. Parse JSON response
7. Evaluate quality
8. Return comprehensive report

**Industry Analysis Flow:** Similar to company analysis but filters by industry field instead of ticker.

---

### Storage (10_storage)
**Purpose:** Data persistence and vector storage

**MilvusManager:**

**Collection Schema:**
```python
Primary Fields:
- id: INT64 (primary key)
- vector: FLOAT_VECTOR (1024 dimensions)

Metadata Fields:
- ticker: VARCHAR(20)
- headline: VARCHAR(1000)
- summary: VARCHAR(5000)
- url: VARCHAR(500)
- source: VARCHAR(100)
- publish_time: INT64 (Unix timestamp)

Classification Fields:
- event_type: VARCHAR(50)
- event_confidence: FLOAT
- industry: VARCHAR(50)
- main_entity: VARCHAR(20)
- industry_confidence: FLOAT
- sentiment_polarity: VARCHAR(20)
- sentiment_intensity: VARCHAR(20)
- sentiment_confidence: FLOAT
- primary_impact: VARCHAR(50)
- business_impacts: VARCHAR(200)
```

**Index Configuration:**
- Index Type: IVF_FLAT
- Metric: COSINE similarity
- nlist: 128

**Operations:**
- `init_collection()` - Create/recreate collection
- `insert_batch()` - Bulk insertion
- `insert_news()` - Single news insertion
- `check_duplicate()` - Similarity-based deduplication
- `search_with_filters()` - Filtered vector search
- `get_statistics()` - Collection stats

**NewsCollectorService:**
- Scheduled news collection from Finnhub
- Automatic pipeline triggering
- Error handling and retry logic
- Logging and monitoring

---

### Report Generation (11_report)
**Purpose:** Generate structured analysis reports

**Report Types:**
1. **Raw Analysis Report** (`company_analysis_*.json`)
   - Complete RAG retrieval results
   - LLM analysis output
   - News statistics
   - Quality evaluation

2. **Enhanced Report** (`enhanced_report_*.json`)
   - Core metrics extraction
   - Sentiment analysis summary
   - Full LLM analysis (parsed JSON)
   - Recent headlines
   - Metadata (timestamp, version)

**Output Structure:**
```
output/
├── AAPL_Apple_Inc/
│   ├── company_analysis_cloud.json
│   ├── enhanced_report_cloud.json
│   └── impact_analysis_prompt_cloud.txt
├── MSFT_Microsoft/
│   ├── company_analysis_local.json
│   ├── enhanced_report_local.json
│   └── impact_analysis_prompt_local.txt
```

**Generation Process:**
1. Call RAGService.analyze_company() or analyze_industry()
2. Extract core metrics from raw data
3. Analyze sentiment distribution
4. Parse LLM raw_response to JSON
5. Build enhanced report structure
6. Save to company-specific folder
7. Save prompt for debugging/reference

**Cloud vs Local Mode:**
- File naming includes mode suffix
- Same structure, different model backend
- Allows comparison between models

---

### Utilities (12_utils)
**Logging Configuration:**
- Loguru-based logging
- Rotating file logs (daily rotation, 7-day retention)
- Console output with colors
- Structured log format
- Separate logs per module

**Log Locations:**
```
01_backend/logs/backend_{time}.log
news_collector_service.log
```

---

## Data Flow

### 1. News Collection Flow
```
Finnhub API → News Collector Script → News Processor Pipeline → Data Validation → 
BGE-M3 Embedding → Deduplication Check → 4-Layer Classification → Milvus Insertion
```

### 2. User Query Flow
```
User Query → Frontend React App → FastAPI Backend → Agent Service → 
FinancialAgent → Intent Recognition → Intent Processor → Intent Routing → 
[RAG Service] → Milvus Search → Build Prompt → LLM Client → 
Analysis → Parse JSON → Quality Evaluator → Save to Disk → Return to User
```

### 3. Memory Flow
```
User Interaction → Importance Check → Long/Short Term Storage → 
Recall Query → Semantic/Keyword Search → Format Context → LLM Prompt
```

---

## Technology Stack

### Backend
- **Framework:** FastAPI 0.104+
- **Language:** Python 3.10+
- **ASGI Server:** Uvicorn
- **Validation:** Pydantic v2
- **Logging:** Loguru

### Frontend
- **Framework:** React 18
- **Language:** TypeScript 5.x
- **UI Library:** Ant Design 5
- **Build Tool:** Vite 5
- **Routing:** React Router 6
- **HTTP Client:** Axios
- **Date Handling:** Day.js

### AI/ML
- **Embedding Model:** BGE-M3 (BAAI/bge-m3)
- **LLM (Cloud):** Qwen Plus (DashScope)
- **LLM (Local):** Ollama (qwen3.5:9b, etc.)
- **Vector Database:** Milvus 2.3+
- **Search:** BM25 (Rank-BM25)

### Data Sources
- **Market Data:** Finnhub API
- **News:** Finnhub News Endpoint

### Storage
- **Vector DB:** Milvus (Standalone)
- **File System:** JSON reports

### Development Tools
- **Testing:** pytest, pytest-asyncio
- **Package Management:** pip, npm
- **Environment:** python-dotenv

---

## Deployment Architecture

### Development Environment
```
┌─────────────────────────────────────┐
│         Developer Machine           │
├─────────────────────────────────────┤
│                                     │
│  Frontend (Port 3000)               │
│  ↓                                  │
│  Backend (Port 8000)                │
│  ↓                                  │
│  Milvus (Port 19530)                │
│  ↓                                  │
│  Ollama (Port 11434)                │
│                                     │
└─────────────────────────────────────┘
```

### Production Architecture (Recommended)
```
Load Balancer (Nginx/ALB)
       ↓
┌──────────────┬──────────────┐
│   Frontend   │   Frontend   │
│  Instance 1  │  Instance 2  │
└──────┬───────┴───────┬──────┘
       ↓               ↓
┌──────┬──────┬───────┬──────┬──────┐
│  BE1 │  BE2 │  BE3  │Ollama│Ollama│
│ FastAPI    │ Cloud  │Server│Server│
│ Instances  │ LLM    │  1   │  2   │
└──────┬──────┴───────┬──────┴──────┘
       ↓               ↓
┌─────────────────────────────────────┐
│         Data Tier                   │
├─────────────────────────────────────┤
│ Milvus Cluster │ MySQL DB │ S3     │
│                │          │ Storage│
└─────────────────────────────────────┘
```

### Docker Services
**Milvus Standalone:**
```bash
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  milvusdb/milvus:latest \
  milvus run standalone
```

**Ollama:**
```bash
docker run -d \
  --gpus all \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  ollama/ollama:latest
```

---

## Design Patterns

### 1. **Lazy Initialization**
Components are initialized on first use to avoid circular dependencies and reduce startup time.
```python
def chat(self, message: str):
    if not self._initialized:
        self.initialize()
    # ... process
```

### 2. **Service Locator**
Centralized access to services through dependency injection.
```python
agent_service = AgentService()
news_service = NewsService()
```

### 3. **Strategy Pattern**
Different LLM backends (cloud/local) selected at runtime.
```python
def create_llm_client(model: str, use_cloud: bool = None):
    if use_cloud or (use_cloud is None and is_cloud_model(model)):
        return CloudLLMClient(model)
    else:
        return LocalLLMClient(model)
```

### 4. **Template Method**
Prompt templates defined in YAML, rendered at runtime.
```python
prompt = prompt_loader.render_template(
    'company_analysis',
    ticker=ticker,
    company_name=company_name,
    # ... variables
)
```

### 5. **Observer Pattern**
Logging throughout the system for observability.
```python
logger.info("✅ Component initialized")
logger.error("❌ Operation failed")
```

### 6. **Factory Pattern**
Intent handlers created based on intent type.
```python
handlers = {
    IntentType.COMPANY_ANALYSIS: self._handle_company_analysis,
    IntentType.NEWS_QUERY: self._handle_news_query,
    # ...
}
handler = handlers.get(intent.intent_type)
```

### 7. **Repository Pattern**
MilvusManager abstracts vector database operations.
```python
milvus.insert_news(news_data)
results = milvus.search_with_filters(query_vector, filters)
```

---

## Key Features

### 1. **Multi-Modal Intent Recognition**
- Rule-based pattern matching for common queries
- LLM-based understanding for complex queries
- Confidence scoring and fallback mechanisms
- Entity extraction (tickers, companies, industries, time ranges)

### 2. **Hybrid Memory System**
- Short-term: Session-scoped, fast access
- Long-term: Persistent, semantic search
- Automatic importance-based routing
- Context recall for personalized responses

### 3. **Four-Layer News Classification**
- Event type identification
- Industry categorization
- Sentiment analysis (polarity + intensity)
- Business impact assessment

### 4. **Intelligent RAG Retrieval**
- Vector similarity search (cosine)
- BM25 keyword matching
- Hybrid ranking with configurable weights
- Multi-dimensional filtering (event type, industry, sentiment)

### 5. **Dual LLM Support**
- **Cloud Mode:** Qwen Plus via DashScope API
  - Higher accuracy
  - No local GPU required
  - API cost involved
  
- **Local Mode:** Ollama with open-source models
  - Privacy-preserving
  - No API costs
  - Requires GPU for best performance

### 6. **Quality Evaluation Framework**
- Six-dimensional assessment
- Automated scoring (0-100)
- Letter grades (A-F)
- Issue detection and improvement suggestions
- Ensures analysis meets quality standards

### 7. **Comprehensive Analysis Reports**
- Multi-dimensional company analysis:
  - Business impact
  - Financial metrics
  - Competitive landscape
  - Strategic implications
  - Future outlook (short/medium/long term)
  - Risk assessment
  - Stakeholder impact

- Industry analysis:
  - Market overview
  - Industry trends
  - Competitive dynamics
  - Policy & regulatory environment
  - Technological innovation
  - Supply chain analysis
  - Investment opportunities
  - Risk factors

### 8. **Source Traceability**
- All analysis includes source URLs
- Citations in format: `[Source: URL]`
- Enables fact-checking and verification
- Transparent reasoning

### 9. **Real-Time News Processing**
- Automated collection from Finnhub
- Immediate embedding and classification
- Deduplication via vector similarity
- Ready for analysis within seconds

### 10. **Conversational Interface**
- Natural language queries
- Multi-turn conversations
- Context preservation
- Clarification when needed
- Friendly error messages

---

## Performance Considerations

### Optimization Strategies
1. **Batch Processing**
   - News ingestion in batches (default: 100)
   - Reduces database round-trips
   - Improves throughput

2. **Vector Indexing**
   - IVF_FLAT index with nlist=128
   - Balanced speed/accuracy trade-off
   - Suitable for medium-scale datasets

3. **Caching**
   - Session data in memory
   - Prompt templates loaded once
   - LLM client reused across requests

4. **Lazy Loading**
   - Components initialized on demand
   - Reduces memory footprint
   - Faster startup time

5. **Asynchronous Operations**
   - FastAPI async endpoints
   - Non-blocking I/O
   - Better concurrency handling

### Bottlenecks
1. **LLM Inference**
   - Cloud: API latency (~2-5 seconds)
   - Local: GPU-dependent (~5-15 seconds)
   - Mitigation: Async processing, streaming responses

2. **Vector Search**
   - Large collections slow down search
   - Mitigation: Proper indexing, filtering before search

3. **Embedding Generation**
   - BGE-M3 is computationally intensive
   - Mitigation: Batch encoding, GPU acceleration

---

## Security Considerations
1. **API Keys**
   - Stored in `.env` file
   - Never committed to version control
   - Use environment variables in production

2. **CORS Configuration**
   - Restricted to known origins
   - Configurable via settings

3. **Input Validation**
   - Pydantic schemas enforce types
   - Sanitize user inputs
   - Prevent injection attacks

4. **Error Handling**
   - Generic error messages to users
   - Detailed logs for debugging
   - No sensitive data in responses

---

## Monitoring & Observability

### Logging Strategy
**Log Levels:**
- `INFO` - Normal operations
- `WARNING` - Potential issues
- `ERROR` - Failures requiring attention
- `DEBUG` - Detailed debugging (development only)

**Log Rotation:**
- Daily rotation
- 7-day retention
- Compressed archives

**Key Metrics to Monitor:**
- Request latency
- LLM response time
- Milvus query performance
- Error rates
- News ingestion rate
- Memory usage

---

## Future Enhancements

### Planned Features
1. **Streaming Responses**
   - Real-time token streaming from LLM
   - Progressive UI updates
   - Better user experience

2. **Advanced Caching**
   - Redis for session storage
   - Response caching for repeated queries
   - Embedding cache

3. **Multi-User Support**
   - User authentication
   - Role-based access control
   - Personalized watchlists

4. **Enhanced Visualization**
   - Interactive charts
   - Trend graphs
   - Comparison dashboards

5. **Additional Data Sources**
   - SEC filings
   - Social media sentiment
   - Analyst ratings

6. **Automated Trading Signals**
   - Buy/sell recommendations
   - Risk alerts
   - Portfolio optimization

7. **Mobile App**
   - React Native implementation
   - Push notifications
   - Offline mode

---

## Troubleshooting

### Common Issues
**1. Milvus Connection Failed**
```
Solution: Ensure Milvus is running
docker ps | grep milvus
docker start milvus-standalone
```

**2. Ollama Model Not Found**
```
Solution: Pull the model
ollama pull qwen3.5:9b
```

**3. High Memory Usage**
```
Solution: Reduce batch size or use quantization
use_quantization=True in report generation
```

**4. Slow LLM Responses**
```
Solution: Switch to cloud mode or optimize prompt length
use_cloud=True for faster inference
```

**5. Duplicate News**
```
Solution: Adjust duplicate threshold in config
DUPLICATE_THRESHOLD = 0.95 (increase to be stricter)
```

---

## Contributing

### Code Standards
- **Python:** PEP 8 compliance
- **TypeScript:** Strict mode enabled
- **Documentation:** Docstrings for all public methods
- **Testing:** Unit tests for critical paths
- **Commits:** Conventional commit messages

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Run linting and tests
5. Submit pull request
6. Code review
7. Merge to main

---

## Glossary
- **RAG (Retrieval-Augmented Generation):** Technique combining retrieval from knowledge base with LLM generation
- **Vector Embedding:** Numerical representation of text capturing semantic meaning
- **Cosine Similarity:** Metric for measuring similarity between two vectors
- **BM25:** Ranking function for estimating relevance of documents to a search query
- **Intent Recognition:** Process of determining user's intention from natural language
- **Milvus:** Open-source vector database for AI applications
- **Ollama:** Tool for running large language models locally
- **BGE-M3:** BAAI's multilingual embedding model with multi-granularity support

---

## References
- https://fastapi.tiangolo.com/
- https://milvus.io/docs
- https://ollama.ai/docs
- https://arxiv.org/abs/2402.03216
- https://arxiv.org/abs/2309.16609
- https://react.dev/
- https://ant.design/

---

## License
This project is proprietary. All rights reserved.

---

## Contact
For questions or support, please refer to the project documentation or contact the development team.

**Last Updated:** April 27, 2026
**Version:** 1.0.0