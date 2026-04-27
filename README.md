# Financial Agent V1

Intelligent Financial Analysis Assistant - A comprehensive financial intelligence system powered by RAG (Retrieval-Augmented Generation) and Large Language Models.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Overview

Financial Agent V1 is an advanced AI-powered financial analysis platform that combines cutting-edge technologies including vector databases, multi-layer news classification, hybrid retrieval systems, and dual-mode LLM support to deliver comprehensive company and industry insights.

### Key Capabilities

- 🎯 **Intelligent Intent Recognition** - Understands natural language queries with high accuracy
- 📊 **Deep Company Analysis** - Multi-dimensional assessment with quality evaluation
- 🏭 **Industry Trend Analysis** - Comprehensive sector-wide insights
- 📰 **Real-time News Processing** - Automated collection, classification, and analysis
- 💬 **Conversational Interface** - Natural multi-turn conversations with context memory
- 📈 **Quality Assurance** - Six-dimensional evaluation framework ensuring reliable analysis
- 🔍 **Source Traceability** - All insights backed by verifiable sources

---

## 🚀 Technology Stack

### Backend
- **Framework**: FastAPI 0.104+ with async support
- **Language**: Python 3.10+
- **Vector Database**: Milvus 2.3+ (IVF_FLAT index, COSINE similarity)
- **Embedding Model**: BGE-M3 (1024 dimensions)
- **LLM Support**: 
  - Cloud: Qwen Plus (DashScope API)
  - Local: Ollama (qwen3.5:9b, etc.)
- **Search Engine**: Hybrid retrieval (Vector + BM25)
- **External APIs**: Finnhub (market data & news)

### Frontend
- **Framework**: React 18 with TypeScript 5.x
- **UI Library**: Ant Design 5
- **Build Tool**: Vite 5
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Routing**: React Router 6

### Infrastructure
- **ASGI Server**: Uvicorn
- **Validation**: Pydantic v2
- **Logging**: Loguru with rotation
- **Testing**: pytest, pytest-asyncio

---

## 📁 Project Structure

```
financial_agent_V1/
│
├── 01_backend/                    # FastAPI Backend Service
│   ├── api/                       # API Routes & Endpoints
│   │   └── routes.py              # RESTful API definitions
│   ├── core/                      # Core Configuration
│   │   └── config.py              # Settings & environment vars
│   ├── models/                    # Data Models
│   │   └── schemas.py             # Pydantic request/response schemas
│   ├── services/                  # Business Logic
│   │   ├── agent_service.py       # Agent orchestration
│   │   └── news_service.py        # News query service
│   ├── logs/                      # Application Logs
│   ├── main.py                    # FastAPI entry point
│   └── requirements.txt           # Python dependencies
│
├── 02_frontend/                   # React Frontend Application
│   ├── public/                    # Static Assets
│   ├── src/
│   │   ├── components/            # Reusable UI Components
│   │   │   ├── DimensionCard      # Analysis dimension display
│   │   │   ├── Layout             # Main layout wrapper
│   │   │   ├── NewsList           # News article listing
│   │   │   ├── QualityReport      # Quality evaluation view
│   │   │   └── StorylineView      # Event timeline
│   │   ├── pages/                 # Page Components
│   │   │   ├── Home               # Landing page
│   │   │   ├── CompanyAnalysis    # Company analysis page
│   │   │   ├── IndustryAnalysis   # Industry analysis page
│   │   │   └── Chat               # Conversational interface
│   │   ├── services/              # API Client
│   │   │   └── api.ts             # Axios configuration
│   │   ├── types/                 # TypeScript Definitions
│   │   └── App.tsx                # Root component
│   ├── package.json               # Node dependencies
│   ├── tsconfig.json              # TypeScript config
│   └── vite.config.ts             # Vite build config
│
├── 03_agent/                      # Agent Core
│   └── agent_core.py              # FinancialAgent implementation
│
├── 04_API/                        # External API Clients
│   ├── finnhub/                   # Finnhub SDK (auto-generated)
│   ├── finnhub_client.py          # Finnhub wrapper
│   └── validator.py               # Input validation
│
├── 05_config/                     # Configuration Management
│   └── settings.py                # Centralized settings class
│
├── 06_intent/                     # Intent Recognition System
│   ├── prompts/                   # Intent recognition prompts
│   │   └── intent_recognition.yaml
│   ├── intent_recognizer.py       # Rule-based recognizer
│   ├── llm_intent_recognizer.py   # LLM-based recognizer
│   └── intent_processor.py        # Intent routing & handling
│
├── 07_memory/                     # Memory Management System
│   ├── memory_manager.py          # Unified memory manager
│   ├── short_term_memory.py       # Session-based memory
│   ├── long_term_memory.py        # Persistent memory (Milvus)
│   └── memory_types.py            # Memory type definitions
│
├── 08_pipeline/                   # News Processing Pipeline
│   ├── embedding.py               # BGE-M3 embedding engine
│   ├── classifier.py              # 4-layer news classifier
│   └── news_processor.py          # Pipeline orchestrator
│
├── 09_retrieve/                   # RAG & Retrieval System
│   ├── prompts/                   # Analysis prompt templates
│   │   ├── company_analysis.yaml
│   │   └── industry_analysis.yaml
│   ├── rag_service.py             # RAG service interface
│   ├── rag_searcher.py            # Hybrid search engine
│   ├── llm_client.py              # Unified LLM client
│   ├── evaluation.py              # Quality evaluation engine
│   ├── json_convertor.py          # LLM response parser
│   └── prompt_loader.py           # YAML template loader
│
├── 10_storage/                    # Storage Layer
│   ├── milvus_manager.py          # Milvus operations
│   └── news_collector_service.py  # News collection service
│
├── 11_report/                     # Report Generation
│   ├── output/                    # Generated reports (gitignored)
│   └── report_generator.py        # Report generation logic
│
├── 12_utils/                      # Utility Functions
│   └── logging_config.py          # Logging configuration
│
├── 13_tests/                      # Test Suite
│   ├── test_backend_api.py        # API integration tests
│   ├── test_evaluation_module.py  # Evaluation tests
│   ├── test_industry_analysis.py  # Industry analysis tests
│   └── test_llm_intent_recognition.py
│
├── 14_scripts/                    # Operational Scripts
│   ├── collect_news.py            # Full news collection
│   ├── quick_collect.py           # Quick news collection
│   ├── recreate_long_term_memory.py  # Memory rebuild
│   └── scheduler.py               # Scheduled tasks
│
├── 15_docs/                       # Documentation
│   ├── API.md                     # API documentation
│   ├── ARCHITECTURE.md            # Architecture overview
│   └── README.md                  # This file
│
├── .env                           # Environment variables (gitignored)
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Root Python dependencies
└── pytest.ini                     # Pytest configuration
```

---

## 🛠️ Installation Guide

### Prerequisites

Before installation, ensure you have:

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **Docker**: For Milvus deployment
- **Git**: For version control
- **GPU** (Optional): For local LLM inference (CUDA-compatible)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd financial_agent_V1
```

### Step 2: Setup Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=financial_agent

# Milvus Vector Database
MILVUS_URI=http://localhost:19530

# LLM Configuration
DEFAULT_LLM_MODEL=qwen-plus
QWEN_CLOUD_MODEL=qwen-plus
OLLAMA_MODEL=qwen3.5:9b

# API Keys
FINNHUB_API_KEY=your_finnhub_api_key
DASHSCOPE_API_KEY=your_dashscope_api_key

# Analysis Parameters
ANALYSIS_DAYS=7
LLM_TEMPERATURE=0.7
RAG_TOP_K=30
```

**Obtaining API Keys:**
- **Finnhub**: Sign up at [finnhub.io](https://finnhub.io/) for free API key
- **DashScope**: Register at [Alibaba Cloud DashScope](https://dashscope.aliyun.com/) for Qwen API access

### Step 3: Start Milvus Vector Database

```bash
# Pull and run Milvus standalone
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest \
  milvus run standalone

# Verify Milvus is running
docker ps | grep milvus
```

### Step 4: Setup Backend

```bash
# Navigate to backend directory
cd 01_backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

**Interactive API Docs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Step 5: Setup Frontend

```bash
# Navigate to frontend directory
cd 02_frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### Step 6: (Optional) Setup Local LLM with Ollama

For local model inference without API costs:

```bash
# Install Ollama (https://ollama.ai/)
# Then pull desired model
ollama pull qwen3.5:9b

# Verify Ollama is running
ollama list

# Test the model
ollama run qwen3.5:9b "Hello!"
```

Ollama runs on port `11434` by default.

---

## 📖 Quick Start

### Option 1: Using Web Interface

1. Open browser and navigate to `http://localhost:3000`
2. Try sample queries:
   - "Analyze Apple Inc."
   - "Show me technology industry trends"
   - "What's the latest news about Tesla?"

### Option 2: Using API Directly

```bash
# Health check
curl http://localhost:8000/health

# Company analysis
curl -X POST http://localhost:8000/api/v1/analyze/company \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "days": 7,
    "use_cloud": true
  }'

# Chat with agent
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How is Apple performing recently?",
    "user_id": "user123"
  }'
```

### Option 3: Using Python SDK

```python
import sys
sys.path.insert(0, '03_agent')

from agent_core import FinancialAgent

# Initialize agent
agent = FinancialAgent(
    user_id="user1",
    use_cloud_llm=True,  # True for cloud, False for local
    verbose=True
)

# Start session
agent.start_session()

# Chat conversation
result = agent.chat("Analyze Apple's recent performance")
print(result['response']['message'])

# Direct company analysis
result = agent.analyze_company(
    ticker="AAPL",
    company_name="Apple Inc.",
    days=7
)

if result['success']:
    print(f"Analysis complete!")
    print(f"Report saved to: {result['result'].get('report_path')}")

# Query news
news_result = agent.query_news(ticker="TSLA", days=3, limit=10)
print(f"Found {news_result['count']} news items")

# End session
agent.end_session()
agent.close()
```

---

## 🎯 Main Features

### 1. Intelligent Intent Recognition

The system automatically understands user intent from natural language:

**Supported Intents:**
- Company analysis requests
- Industry trend queries
- News retrieval
- Stock comparisons
- Watchlist management
- General financial questions

**Example Queries:**
```
✅ "Analyze Apple Inc."
✅ "How is the technology industry doing?"
✅ "Show me recent news about Tesla"
✅ "Compare Microsoft and Google"
✅ "Add AAPL to my watchlist"
```

### 2. Deep Company Analysis

Comprehensive multi-dimensional analysis including:

- **Business Impact Assessment** - Score -10 to +10 with justification
- **Financial Metrics Analysis** - Performance indicators and trends
- **Competitive Landscape** - Market position and rivals
- **Strategic Implications** - Long-term strategic alignment
- **Future Outlook** - Short/medium/long-term predictions
- **Risk Analysis** - Identification and mitigation strategies
- **Stakeholder Impact** - Effects on investors, employees, customers

**Quality Evaluation:**
Each analysis is automatically evaluated on six dimensions:
- Completeness (coverage of all aspects)
- Traceability (source citations)
- Consistency (logical coherence)
- Depth (insight quality)
- Timeliness (information recency)
- Balance (multiple viewpoints)

Overall score: 0-100 with letter grades (A-F)

### 3. Industry Analysis

Sector-wide comprehensive analysis covering:

- Market overview and size
- Growth trends and patterns
- Competitive dynamics
- Policy and regulatory environment
- Technological innovations
- Supply chain analysis
- Investment opportunities
- Risk factors

### 4. Real-time News Processing

Automated news pipeline:

1. **Collection** - Fetch from Finnhub API
2. **Embedding** - BGE-M3 vectorization (1024 dimensions)
3. **Deduplication** - Cosine similarity check (threshold: 0.95)
4. **4-Layer Classification**:
   - Event type (earnings, M&A, product launch, etc.)
   - Industry categorization (8 sectors)
   - Sentiment analysis (polarity + intensity)
   - Business impact assessment
5. **Storage** - Milvus vector database

### 5. Hybrid RAG Retrieval

Combines best of both worlds:

- **Vector Search** - Semantic understanding (weight: 0.7)
- **BM25 Search** - Keyword matching (weight: 0.3)
- **Multi-dimensional Filtering** - By event type, industry, sentiment
- **Configurable Top-K** - Default: 30 results

### 6. Dual LLM Mode

**Cloud Mode (Qwen Plus):**
- ✅ Higher accuracy
- ✅ No GPU required
- ✅ Faster inference
- ❌ API costs apply
- ❌ Requires internet

**Local Mode (Ollama):**
- ✅ Privacy-preserving
- ✅ No API costs
- ✅ Works offline
- ❌ Requires GPU for best performance
- ❌ Slower than cloud

Switch modes easily:

```python
# Cloud mode
agent = FinancialAgent(use_cloud_llm=True)

# Local mode
agent = FinancialAgent(use_cloud_llm=False)

# Auto-detect (default)
agent = FinancialAgent()
```

### 7. Memory System

**Short-Term Memory:**
- Session-scoped conversation history
- Fast in-memory access
- Automatic cleanup

**Long-Term Memory:**
- Persistent storage in Milvus
- Semantic search capability
- Stores user preferences, past analyses, watchlists
- Importance-based retention (0-1 scale)

### 8. Source Traceability

All analysis includes:
- Direct source URLs
- Inline citations: `[Source: URL]`
- Reference lists
- Enables fact-checking

### 9. Watchlist Management

Track favorite stocks:

```python
# Add to watchlist
agent.memory.add_to_watchlist("AAPL", "Apple Inc.")

# View watchlist
watchlist = agent.memory.get_watchlist()
```

### 10. Report Generation

Automatic report saving:

```
output/
├── AAPL_Apple_Inc/
│   ├── company_analysis_cloud.json
│   ├── enhanced_report_cloud.json
│   └── impact_analysis_prompt_cloud.txt
└── MSFT_Microsoft/
    ├── company_analysis_local.json
    ├── enhanced_report_local.json
    └── impact_analysis_prompt_local.txt
```

---

## 🔧 Configuration

### Environment Variables (.env)

**Database Settings:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=financial_agent
```

**Milvus Configuration:**
```env
MILVUS_URI=http://localhost:19530
```

**LLM Models:**
```env
# Default model (auto-selected)
DEFAULT_LLM_MODEL=qwen-plus

# Cloud model (DashScope)
QWEN_CLOUD_MODEL=qwen-plus

# Local model (Ollama)
OLLAMA_MODEL=qwen3.5:9b
```

**API Keys:**
```env
FINNHUB_API_KEY=sk_xxxxxxxxxxxx
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
```

**Analysis Parameters:**
```env
# Days to analyze (default)
ANALYSIS_DAYS=7

# LLM temperature (creativity vs precision)
LLM_TEMPERATURE=0.7

# Number of documents to retrieve
RAG_TOP_K=30

# Duplicate detection threshold (0-1)
DUPLICATE_THRESHOLD=0.95

# Search result limit
SEARCH_LIMIT=10

# Search relevance threshold
SEARCH_THRESHOLD=0.7
```

**Batch Processing:**
```env
BATCH_SIZE=100
VECTOR_DIMENSION=1024
```

### Prompt Templates

Customize analysis prompts in YAML format:

**Company Analysis:** `09_retrieve/prompts/company_analysis.yaml`
**Industry Analysis:** `09_retrieve/prompts/industry_analysis.yaml`

Example customization:
```yaml
max_recent_headlines: 5
max_representative_news: 12
headline_max_length: 100
summary_max_length: 200
representative_per_type: 2
```

---

## 📊 Usage Examples

### Example 1: Company Analysis via Web UI

1. Navigate to `http://localhost:3000`
2. Click "Company Analysis"
3. Enter ticker: `AAPL`
4. Select analysis period: `7 days`
5. Choose model: `Cloud` or `Local`
6. Click "Analyze"
7. View results:
   - Analysis dimensions with scores
   - Quality evaluation report
   - Event timeline
   - Source references

### Example 2: Conversational Query

```python
from 03_agent.agent_core import FinancialAgent

agent = FinancialAgent(user_id="investor_001", use_cloud_llm=True)
agent.start_session()

# Multi-turn conversation
response1 = agent.chat("What do you know about Apple?")
print(response1['response']['message'])

response2 = agent.chat("How does it compare to Microsoft?")
print(response2['response']['message'])

response3 = agent.chat("Show me recent news about both companies")
print(response3['response']['message'])

agent.end_session()
```

### Example 3: Industry Analysis

```python
# Via API
import requests

response = requests.post(
    'http://localhost:8000/api/v1/analyze/industry',
    json={
        'industry': 'technology',
        'industry_name': 'Technology Sector',
        'days': 30,
        'use_cloud': True
    }
)

result = response.json()
print(f"Industry: {result['industry_name']}")
print(f"Total news analyzed: {result['result']['total_news']}")
print(f"Quality score: {result['result']['quality_evaluation']['overall_score']}")
```

### Example 4: Batch News Collection

```bash
# Collect news for multiple tickers
python 14_scripts/collect_news.py --tickers AAPL,MSFT,GOOGL,TSLA --days 7

# Quick collection (last 24 hours)
python 14_scripts/quick_collect.py --limit 100
```

### Example 5: Custom Analysis Parameters

```python
agent = FinancialAgent(
    user_id="analyst_pro",
    use_cloud_llm=True,
    device='cuda',  # For local mode with GPU
    verbose=True
)

# Analyze with custom parameters
result = agent.analyze_company(
    ticker="NVDA",
    company_name="NVIDIA Corporation",
    days=14,  # Last 2 weeks
)

# Access detailed results
if result['success']:
    analysis = result['result']['llm_analysis']
    
    # Business impact score
    biz_impact = analysis['business_impact']
    print(f"Business Impact Score: {biz_impact['score']}/10")
    print(f"Justification: {biz_impact['score_justification']}")
    
    # Future outlook
    outlook = analysis['future_outlook']
    print(f"Short-term: {outlook['short_term_impact']}")
    print(f"Medium-term: {outlook['medium_term_impact']}")
    print(f"Long-term: {outlook['long_term_impact']}")
    
    # Quality metrics
    quality = result['result']['quality_evaluation']
    print(f"Overall Grade: {quality['grade']}")
    print(f"Issues Found: {len(quality['issues'])}")
```

---

## 🧪 Testing

Run test suite:

```bash
# All tests
pytest 13_tests/ -v

# Specific test file
pytest 13_tests/test_backend_api.py -v

# With coverage
pytest 13_tests/ --cov=01_backend --cov-report=html
```

**Test Coverage:**
- API endpoint functionality
- Intent recognition accuracy
- Evaluation module correctness
- Industry analysis workflow
- LLM intent recognition

---

## 📝 API Endpoints

Complete API documentation available at `http://localhost:8000/docs`

**Key Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/chat` | Chat with agent |
| POST | `/api/v1/analyze/company` | Company analysis |
| POST | `/api/v1/analyze/industry` | Industry analysis |
| POST | `/api/v1/news/query` | Query news |
| POST | `/api/v1/watchlist` | Manage watchlist |
| GET | `/api/v1/watchlist/{user_id}` | Get watchlist |

See [API.md](API.md) for detailed documentation.

---

## 🏗️ Architecture

For detailed architecture overview, see [ARCHITECTURE.md](ARCHITECTURE.md)

**High-Level Flow:**

```
User Query → Intent Recognition → Memory Recall → RAG Retrieval → 
LLM Analysis → Quality Evaluation → Report Generation → Response
```

**News Processing Flow:**

```
Finnhub API → Validation → BGE-M3 Embedding → Deduplication → 
4-Layer Classification → Milvus Storage → Ready for Analysis
```

---

## 🔍 Troubleshooting

### Common Issues

**1. Milvus Connection Failed**

```
Error: Milvus connection failed
```

**Solution:**
```bash
# Check if Milvus is running
docker ps | grep milvus

# Start Milvus if stopped
docker start milvus-standalone

# Or restart
docker restart milvus-standalone
```

**2. Ollama Model Not Found**

```
Error: model "qwen3.5:9b" not found
```

**Solution:**
```bash
# Pull the model
ollama pull qwen3.5:9b

# Verify installation
ollama list
```

**3. High Memory Usage**

**Solution:**
```python
# Use quantization for local models
agent = FinancialAgent(use_cloud_llm=False)
# Quantization enabled by default (4-bit)

# Or reduce batch size in .env
BATCH_SIZE=50
```

**4. Slow LLM Responses**

**Solution:**
```python
# Switch to cloud mode for faster inference
agent = FinancialAgent(use_cloud_llm=True)

# Or optimize prompt length
RAG_TOP_K=15  # Reduce from default 30
```

**5. Duplicate News Being Stored**

**Solution:**
```env
# Increase threshold in .env (more strict)
DUPLICATE_THRESHOLD=0.98
```

**6. Port Already in Use**

```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>

# Or change port in config
PORT=8001  # In .env
```

**7. Missing API Keys**

```
Error: DashScope API key not configured
```

**Solution:**
```env
# Ensure .env file has correct keys
DASHSCOPE_API_KEY=sk-your-actual-key
FINNHUB_API_KEY=sk-your-actual-key

# Restart backend after changes
```

**8. CUDA Out of Memory**

```
Error: CUDA out of memory
```

**Solution:**
```python
# Use CPU instead
agent = FinancialAgent(device='cpu')

# Or use smaller model
OLLAMA_MODEL=qwen2.5:7b  # Instead of 9b

# Enable quantization (already default)
use_quantization=True
```

### Debugging Tips

**Enable Verbose Logging:**
```python
agent = FinancialAgent(verbose=True)
```

**Check Logs:**
```bash
# Backend logs
tail -f 01_backend/logs/backend_*.log

# News collector logs
tail -f news_collector_service.log
```

**Test Individual Components:**
```python
# Test intent recognition
from 06_intent.intent_recognizer import IntentRecognizer
recognizer = IntentRecognizer()
result = recognizer.recognize("Analyze Apple Inc.")
print(result.to_dict())

# Test RAG retrieval
from 09_retrieve.rag_service import RAGService
rag = RAGService()
results = rag.search(query="Apple earnings", limit=5)
print(f"Found {len(results)} results")
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

**Code Style:**
- Python: Follow PEP 8
- TypeScript: Strict mode enabled
- Add docstrings to all public methods
- Write unit tests for new features

**Commit Messages:**
Use conventional commits:
```
feat: add new feature
fix: bug fix
docs: documentation update
style: code style changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

**Testing:**
- Run tests before submitting PR
- Maintain or improve code coverage
- Add tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **BAAI** for BGE-M3 embedding model
- **Alibaba Cloud** for Qwen LLM and DashScope API
- **Finnhub** for financial data API
- **Milvus** team for vector database
- **FastAPI** and **React** communities

---

## 📞 Support

**Documentation:**
- [API Documentation](API.md)
- [Architecture Guide](ARCHITECTURE.md)

**Issues:**
- GitHub Issues: Report bugs and feature requests

**Contact:**
- Email: [your-email@example.com]
- Discussion Forum: [link if applicable]

---

## 🗺️ Roadmap

### Planned Features (v1.1)
- [ ] Streaming responses from LLM
- [ ] Redis caching layer
- [ ] User authentication & authorization
- [ ] Interactive charts and visualizations
- [ ] Mobile app (React Native)
- [ ] Additional data sources (SEC filings, social media)
- [ ] Automated trading signals
- [ ] Portfolio optimization

### Under Consideration
- Multi-language support
- Real-time market data streaming
- Advanced risk modeling
- Integration with brokerage APIs

---

## 📊 Performance Benchmarks

**Typical Response Times:**

| Operation | Cloud Mode | Local Mode (GPU) |
|-----------|------------|------------------|
| Intent Recognition | ~200ms | ~200ms |
| Company Analysis | 15-30s | 30-60s |
| Industry Analysis | 20-40s | 40-90s |
| News Query | ~500ms | ~500ms |
| Chat Response | 2-5s | 5-15s |

**System Requirements:**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| GPU | None | NVIDIA RTX 3060+ (12GB VRAM) |
| Storage | 50 GB | 100 GB SSD |
| Network | 10 Mbps | 100 Mbps |

---

**Last Updated:** April 27, 2026  
**Version:** 1.0.0  
**Status:** Production Ready

---

Made with ❤️ by the Financial Agent Team