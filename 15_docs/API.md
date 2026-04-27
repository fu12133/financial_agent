# Financial Agent API Documentation

## Overview
The Financial Agent API is a FastAPI-based backend service providing intelligent financial analysis capabilities, including company analysis, industry analysis, news querying, and conversational AI for financial insights.

**Base URL:** `http://localhost:8000/api/v1`
**API Version:** 1.0.0

---

## Table of Contents
- #authentication
- #common-response-format
- #endpoints
  - #health-check
  - #root-endpoint
  - #chat
  - #company-analysis
  - #industry-analysis
  - #news-query
  - #watchlist-management
- #data-models
- #error-handling
- #cors-configuration
- #rate-limiting
- #pagination
- #interactive-api-documentation
- #environment-variables
- #best-practices
- #support-and-contact
- #changelog

---

## Authentication
Currently, the API does not require authentication. All endpoints are publicly accessible. User identification is handled through optional `user_id` parameters in requests.

---

## Common Response Format
All API responses follow a consistent JSON format:

```json
{
  "success": true,
  "timestamp": "2026-04-27T10:30:00.000Z",
  "error": null
}
```

### Common Fields
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates whether the request was successful |
| `timestamp` | string (ISO 8601) | Server timestamp when the response was generated |
| `error` | string or null | Error message if success is false, otherwise null |

---

## Endpoints

### Health Check
#### GET `/health`
Check the health status of the API service.

**Request:**
```
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### Root Endpoint
#### GET `/`
Get basic API information.

**Request:**
```
GET /api/v1/
```

**Response:**
```json
{
  "message": "Financial Agent API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### Chat
#### POST `/chat`
Process natural language queries and provide intelligent responses with intent recognition. Supports various financial queries including company analysis, industry trends, news queries, and general conversation.

**Request:**
```
POST /api/v1/chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Analyze Apple's recent performance",
  "user_id": "default",
  "session_id": "optional-session-id"
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | Yes | - | User's query or message (min length: 1) |
| `user_id` | string | No | `"default"` | User identifier for personalized responses |
| `session_id` | string | No | `null` | Session identifier for conversation context |

**Response:**
```json
{
  "success": true,
  "agent_id": "agent-123",
  "session_id": "session-456",
  "response": {
    "intent": "company_analysis",
    "content": "Based on recent analysis...",
    "data": {}
  },
  "intent": {
    "type": "company_analysis",
    "confidence": 0.95,
    "entities": {
      "ticker": "AAPL"
    }
  },
  "timestamp": "2026-04-27T10:30:00.000Z",
  "error": null
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `agent_id` | string | Identifier of the agent that processed the request |
| `session_id` | string | Session identifier for maintaining conversation context |
| `response` | object | The agent's response containing intent, content, and data |
| `intent` | object | Detected intent with type, confidence score, and extracted entities |
| `timestamp` | string | ISO 8601 timestamp |
| `error` | string or null | Error message if failed |

**Supported Intent Types:**
- `company_analysis` - Company-specific analysis
- `industry_analysis` - Industry trend analysis
- `news_query` - News retrieval
- `stock_comparison` - Stock comparison
- `market_trend` - Market trend analysis
- `sentiment_analysis` - Sentiment analysis
- `watchlist_manage` - Watchlist operations
- `memory_query` - Memory-based queries
- `report_generate` - Report generation
- `general_chat` - General conversation

**Status Codes:**
- `200 OK` - Request processed successfully
- `400 Bad Request` - Invalid input
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the latest news about Tesla?",
    "user_id": "user123"
  }'
```

---

### Company Analysis
#### POST `/analyze/company`
Perform comprehensive analysis of a specific company based on recent news and market data. Generates detailed reports covering business impact, financial metrics, competitive landscape, and future outlook.

**Request:**
```
POST /api/v1/analyze/company
Content-Type: application/json
```

**Request Body:**
```json
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "days": 7,
  "use_cloud": false
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ticker` | string | Yes | - | Stock ticker symbol (e.g., "AAPL", "TSLA") |
| `company_name` | string | No | `null` | Company name (optional, used for validation) |
| `days` | integer | No | `7` | Number of days to analyze (1-365) |
| `use_cloud` | boolean | No | `null` | Whether to use cloud-based LLM model (true) or local Ollama model (false) |

**Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "result": {
    "llm_analysis": {
      "business_impact": {
        "score": 8,
        "score_justification": "Strong positive impact due to...",
        "analysis": "Detailed analysis text with citations...",
        "key_factors": ["Factor 1", "Factor 2"],
        "source_urls": ["url1", "url2"]
      },
      "financial_metrics": {
        "score": 7,
        "analysis": "Financial analysis...",
        "source_urls": ["url1"]
      },
      "competitive_landscape": {
        "score": 6,
        "analysis": "Competitive analysis...",
        "source_urls": ["url1"]
      },
      "strategic_impact": {
        "score": 8,
        "analysis": "Strategic implications...",
        "key_points": ["Point 1", "Point 2"],
        "source_urls": ["url1"]
      },
      "future_outlook": {
        "score": 7,
        "analysis": "Overall future outlook...",
        "short_term_impact": "1-3 months outlook...",
        "medium_term_impact": "3-12 months outlook...",
        "long_term_impact": "1-3 years outlook...",
        "risk_analysis": "Risk assessment...",
        "stakeholder_impact": {
          "investors": "Impact on investors...",
          "employees": "Impact on employees..."
        },
        "source_urls": ["url1"]
      },
      "overall_assessment": {
        "score": 7,
        "summary": "Overall summary...",
        "recommendations": ["Recommendation 1", "Recommendation 2"],
        "source_urls": ["url1"]
      }
    },
    "quality_evaluation": {
      "overall_score": 85,
      "grade": "A",
      "dimensions": {
        "completeness": {
          "score": 90,
          "passed": true
        },
        "traceability": {
          "score": 85,
          "passed": true
        },
        "consistency": {
          "score": 80,
          "passed": true
        },
        "depth": {
          "score": 85,
          "passed": true
        },
        "timeliness": {
          "score": 90,
          "passed": true
        },
        "balance": {
          "score": 80,
          "passed": true
        }
      },
      "issues": [],
      "recommendations": ["Suggestion 1"],
      "passed": true
    },
    "total_news": 45,
    "companies_covered": ["AAPL"]
  },
  "report_path": "/path/to/report.json",
  "timestamp": "2026-04-27T10:30:00.000Z",
  "error": null
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `ticker` | string | Analyzed company ticker |
| `company_name` | string | Company name |
| `result` | object | Analysis results containing LLM analysis and quality evaluation |
| `result.llm_analysis` | object | Detailed analysis across multiple dimensions |
| `result.quality_evaluation` | object | Quality assessment of the analysis |
| `result.total_news` | integer | Total number of news articles analyzed |
| `result.companies_covered` | array | List of companies mentioned in the analysis |
| `report_path` | string | File path to the saved report (JSON format) |
| `timestamp` | string | ISO 8601 timestamp |
| `error` | string or null | Error message if failed |

**Analysis Dimensions:**
Each dimension includes:
- `score`: Integer from -10 to 10
- `score_justification`: Brief explanation of the score (50-100 words)
- `analysis`: Comprehensive analysis text (100-200 words) with source citations
- `key_factors` or `key_points`: Key factors or points identified
- `source_urls`: URLs of sources used for the analysis

**Quality Evaluation Dimensions:**
- **Completeness**: Coverage of all required aspects
- **Traceability**: Proper source citation and attribution
- **Consistency**: Logical coherence throughout the analysis
- **Depth**: Depth of insight and analysis quality
- **Timeliness**: Relevance and recency of information
- **Balance**: Balanced perspective considering multiple viewpoints

**Status Codes:**
- `200 OK` - Analysis completed successfully
- `400 Bad Request` - Invalid ticker or parameters
- `500 Internal Server Error` - Analysis failed

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze/company \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "MSFT",
    "days": 14,
    "use_cloud": true
  }'
```

---

### Industry Analysis
#### POST `/analyze/industry`
Perform comprehensive analysis of a specific industry sector, covering market trends, competitive landscape, policy regulations, technological innovation, and supply chain dynamics.

**Request:**
```
POST /api/v1/analyze/industry
Content-Type: application/json
```

**Request Body:**
```json
{
  "industry": "technology",
  "industry_name": "Technology Sector",
  "days": 7,
  "use_cloud": false
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `industry` | string | Yes | - | Industry code (e.g., "technology", "healthcare", "finance") |
| `industry_name` | string | No | `null` | Human-readable industry name |
| `days` | integer | No | `7` | Number of days to analyze (1-365) |
| `use_cloud` | boolean | No | `null` | Whether to use cloud-based LLM model |

**Response:**
```json
{
  "success": true,
  "industry": "technology",
  "industry_name": "Technology Sector",
  "result": {
    "llm_analysis": {
      "market_overview": {
        "score": 8,
        "score_justification": "Strong market growth driven by...",
        "analysis": "Comprehensive market overview...",
        "key_factors": ["AI adoption", "Cloud computing growth"],
        "source_urls": ["url1", "url2"]
      },
      "industry_trend": {
        "score": 9,
        "analysis": "Industry trend analysis...",
        "key_factors": ["Digital transformation", "Automation"],
        "source_urls": ["url1"]
      },
      "competitive_landscape": {
        "score": 7,
        "analysis": "Competitive dynamics...",
        "key_factors": ["Market concentration", "Entry barriers"],
        "source_urls": ["url1"]
      },
      "policy_regulatory": {
        "score": 6,
        "analysis": "Regulatory environment analysis...",
        "key_factors": ["Data privacy laws", "Antitrust regulations"],
        "source_urls": ["url1"]
      },
      "technological_innovation": {
        "score": 9,
        "analysis": "Technology innovation landscape...",
        "key_factors": ["AI breakthroughs", "Quantum computing"],
        "source_urls": ["url1"]
      },
      "supply_chain": {
        "score": 7,
        "analysis": "Supply chain dynamics...",
        "key_factors": ["Semiconductor availability", "Global logistics"],
        "source_urls": ["url1"]
      },
      "investment_opportunities": {
        "score": 8,
        "analysis": "Investment opportunity analysis...",
        "key_factors": ["Emerging markets", "Growth sectors"],
        "source_urls": ["url1"]
      },
      "risk_factors": {
        "score": -3,
        "analysis": "Key risk factors...",
        "key_factors": ["Geopolitical tensions", "Economic uncertainty"],
        "source_urls": ["url1"]
      },
      "overall_assessment": {
        "score": 7,
        "summary": "Overall industry assessment...",
        "recommendations": ["Recommendation 1"],
        "source_urls": ["url1"]
      }
    },
    "quality_evaluation": {
      "overall_score": 88,
      "grade": "A",
      "dimensions": {
        "completeness": {
          "score": 90,
          "passed": true
        },
        "traceability": {
          "score": 85,
          "passed": true
        },
        "consistency": {
          "score": 88,
          "passed": true
        },
        "depth": {
          "score": 87,
          "passed": true
        },
        "timeliness": {
          "score": 92,
          "passed": true
        },
        "balance": {
          "score": 85,
          "passed": true
        }
      },
      "issues": [],
      "recommendations": [],
      "passed": true
    },
    "total_news": 120,
    "companies_covered": ["AAPL", "MSFT", "GOOGL"]
  },
  "report_path": "/path/to/industry_report.json",
  "timestamp": "2026-04-27T10:30:00.000Z",
  "error": null
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `industry` | string | Industry code |
| `industry_name` | string | Industry name |
| `result` | object | Analysis results |
| `result.llm_analysis` | object | Multi-dimensional industry analysis |
| `result.quality_evaluation` | object | Quality assessment metrics |
| `result.total_news` | integer | Total news articles analyzed |
| `result.companies_covered` | array | Companies mentioned in the analysis |
| `report_path` | string | Path to saved report file |
| `timestamp` | string | ISO 8601 timestamp |
| `error` | string or null | Error message if failed |

**Industry Analysis Dimensions:**
1. **Market Overview**: Current market state, size, and growth
2. **Industry Trend**: Growth patterns and directional trends
3. **Competitive Landscape**: Market structure and competition
4. **Policy & Regulatory**: Government policies and regulations
5. **Technological Innovation**: Technology developments and disruptions
6. **Supply Chain**: Supply chain dynamics and challenges
7. **Investment Opportunities**: Potential investment areas
8. **Risk Factors**: Key risks and challenges
9. **Overall Assessment**: Comprehensive summary and recommendations

**Status Codes:**
- `200 OK` - Analysis completed successfully
- `400 Bad Request` - Invalid industry code or parameters
- `500 Internal Server Error` - Analysis failed

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze/industry \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "healthcare",
    "industry_name": "Healthcare Industry",
    "days": 30
  }'
```

---

### News Query
#### POST `/news/query`
Retrieve recent news articles for a specific stock ticker with sentiment analysis and event classification.

**Request:**
```
POST /api/v1/news/query
Content-Type: application/json
```

**Request Body:**
```json
{
  "ticker": "AAPL",
  "days": 7,
  "limit": 10
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ticker` | string | Yes | - | Stock ticker symbol |
| `days` | integer | No | `7` | Number of days to look back for news |
| `limit` | integer | No | `10` | Maximum number of articles to return (1-100) |

**Response:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "count": 10,
  "news": [
    {
      "id": "news-123",
      "ticker": "AAPL",
      "headline": "Apple Announces New Product Line",
      "summary": "Apple Inc. today announced...",
      "url": "https://example.com/news/123",
      "source": "Reuters",
      "publish_time": 1714204800,
      "sentiment_polarity": "positive",
      "sentiment_intensity": "strong",
      "event_type": "product_launch",
      "industry": "technology"
    }
  ],
  "timestamp": "2026-04-27T10:30:00.000Z",
  "error": null
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `ticker` | string | Queried stock ticker |
| `count` | integer | Number of news articles returned |
| `news` | array | List of news articles |
| `news[].id` | string | Unique news identifier |
| `news[].ticker` | string | Associated stock ticker |
| `news[].headline` | string | News headline |
| `news[].summary` | string | News summary |
| `news[].url` | string | URL to full article |
| `news[].source` | string | News source/publisher |
| `news[].publish_time` | integer | Unix timestamp of publication |
| `news[].sentiment_polarity` | string | Sentiment: "positive", "negative", or "neutral" |
| `news[].sentiment_intensity` | string | Intensity: "strong", "moderate", or "weak" |
| `news[].event_type` | string | Classified event type |
| `news[].industry` | string | Related industry sector |
| `timestamp` | string | ISO 8601 timestamp |
| `error` | string or null | Error message if failed |

**Sentiment Values:**
- **Polarity**: `positive`, `negative`, `neutral`
- **Intensity**: `strong`, `moderate`, `weak`

**Status Codes:**
- `200 OK` - News retrieved successfully
- `400 Bad Request` - Invalid ticker or parameters
- `500 Internal Server Error` - Query failed

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/news/query \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "GOOGL",
    "days": 3,
    "limit": 5
  }'
```

---

### Watchlist Management
#### POST `/watchlist`
Manage user watchlists by adding or removing stock tickers.

**Request:**
```
POST /api/v1/watchlist
Content-Type: application/json
```

**Request Body:**
**Add to Watchlist:**
```json
{
  "action": "add",
  "ticker": "AAPL",
  "company_name": "Apple Inc."
}
```

**Remove from Watchlist:**
```json
{
  "action": "remove",
  "ticker": "AAPL"
}
```

**View Watchlist:**
```json
{
  "action": "view"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | Yes | Operation type: `"add"`, `"remove"`, or `"view"` |
| `ticker` | string | Conditional | Stock ticker (required for add/remove) |
| `company_name` | string | No | Company name (optional, for add operation) |

**Response:**
```json
{
  "success": true,
  "action": "add",
  "watchlist": ["AAPL", "MSFT", "GOOGL"],
  "message": "Successfully added AAPL to watchlist",
  "timestamp": "2026-04-27T10:30:00.000Z"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `action` | string | Performed action |
| `watchlist` | array or null | Updated watchlist (null for view action without user_id) |
| `message` | string | Human-readable result message |
| `timestamp` | string | ISO 8601 timestamp |

**Status Codes:**
- `200 OK` - Operation completed successfully
- `400 Bad Request` - Invalid action or missing parameters
- `500 Internal Server Error` - Operation failed

**Example:**
```bash
# Add to watchlist
curl -X POST http://localhost:8000/api/v1/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add",
    "ticker": "TSLA",
    "company_name": "Tesla Inc."
  }'

# Remove from watchlist
curl -X POST http://localhost:8000/api/v1/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "action": "remove",
    "ticker": "TSLA"
  }'
```

---

#### GET `/watchlist/{user_id}`
Retrieve a user's current watchlist.

**Request:**
```
GET /api/v1/watchlist/default
```

**Parameters:**
| Parameter | Type | Location | Default | Description |
|-----------|------|----------|---------|-------------|
| `user_id` | string | Path | `"default"` | User identifier |

**Response:**
```json
{
  "success": true,
  "user_id": "default",
  "watchlist": ["AAPL", "MSFT", "GOOGL", "TSLA"],
  "timestamp": "2026-04-27T10:30:00.000Z"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `user_id` | string | User identifier |
| `watchlist` | array | List of stock tickers in the watchlist |
| `timestamp` | string | ISO 8601 timestamp |

**Status Codes:**
- `200 OK` - Watchlist retrieved successfully
- `500 Internal Server Error` - Failed to retrieve watchlist

**Example:**
```bash
curl http://localhost:8000/api/v1/watchlist/user123
```

---

## Data Models

### IntentType Enum
Represents different types of user intents that the system can recognize:

```typescript
enum IntentType {
  COMPANY_ANALYSIS = "company_analysis",
  INDUSTRY_ANALYSIS = "industry_analysis",
  NEWS_QUERY = "news_query",
  STOCK_COMPARISON = "stock_comparison",
  MARKET_TREND = "market_trend",
  SENTIMENT_ANALYSIS = "sentiment_analysis",
  WATCHLIST_MANAGE = "watchlist_manage",
  MEMORY_QUERY = "memory_query",
  REPORT_GENERATE = "report_generate",
  GENERAL_CHAT = "general_chat"
}
```

### Request Models

#### ChatRequest
```typescript
interface ChatRequest {
  message: string;        // Min length: 1
  user_id?: string;       // Default: "default"
  session_id?: string;    // Optional
}
```

#### CompanyAnalysisRequest
```typescript
interface CompanyAnalysisRequest {
  ticker: string;        // Required, e.g., "AAPL"
  company_name?: string; // Optional
  days?: number;         // Range: 1-365, Default: 7
  use_cloud?: boolean;   // Optional, null = use default
}
```

#### IndustryAnalysisRequest
```typescript
interface IndustryAnalysisRequest {
  industry: string;      // Required, e.g., "technology"
  industry_name?: string; // Optional
  days?: number;         // Range: 1-365, Default: 7
  use_cloud?: boolean;   // Optional
}
```

#### NewsQueryRequest
```typescript
interface NewsQueryRequest {
  ticker: string;        // Required
  days?: number;         // Default: 7
  limit?: number;        // Range: 1-100, Default: 10
}
```

#### WatchlistRequest
```typescript
interface WatchlistRequest {
  action: string;        // "add", "remove", or "view"
  ticker?: string;       // Required for add/remove
  company_name?: string; // Optional for add
}
```

### Response Models

#### ChatResponse
```typescript
interface ChatResponse {
  success: boolean;
  agent_id?: string;
  session_id?: string;
  response: object;
  intent?: object;
  timestamp: string;
  error?: string;
}
```

#### CompanyAnalysisResponse
```typescript
interface CompanyAnalysisResponse {
  success: boolean;
  ticker: string;
  company_name: string;
  result?: object;
  report_path?: string;
  timestamp: string;
  error?: string;
}
```

#### IndustryAnalysisResponse
```typescript
interface IndustryAnalysisResponse {
  success: boolean;
  industry: string;
  industry_name: string;
  result?: object;
  report_path?: string;
  timestamp: string;
  error?: string;
}
```

#### NewsResponse
```typescript
interface NewsResponse {
  success: boolean;
  ticker: string;
  count: number;
  news: Array<NewsItem>;
  timestamp: string;
  error?: string;
}
```

#### WatchlistResponse
```typescript
interface WatchlistResponse {
  success: boolean;
  action: string;
  watchlist?: Array<string>;
  message: string;
  timestamp: string;
}
```

---

## Error Handling
The API uses standard HTTP status codes and returns error details in the response body.

### HTTP Status Codes
| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side error |

### Error Response Format
```json
{
  "error": "Internal server error",
  "detail": "Specific error message describing what went wrong"
}
```

### Common Errors
**Invalid Ticker Symbol:**
```json
{
  "error": "Bad Request",
  "detail": "Invalid ticker symbol: XYZ"
}
```

**Analysis Timeout:**
```json
{
  "error": "Internal server error",
  "detail": "Analysis timed out after 300 seconds"
}
```

**Database Connection Error:**
```json
{
  "error": "Internal server error",
  "detail": "Failed to connect to database"
}
```

---

## CORS Configuration
The API supports Cross-Origin Resource Sharing (CORS) with the following configuration:

**Allowed Origins:**
- `http://localhost:3000`
- `http://localhost:5173`

**Allowed Methods:**
- All methods (`*`)

**Allowed Headers:**
- All headers (`*`)

**Credentials:**
- Allowed

To modify CORS settings, update the `.env` file or the `Settings` class in `01_backend/core/config.py`.

---

## Rate Limiting
Currently, the API does not implement rate limiting. However, long-running operations like company and industry analysis may timeout after 300 seconds (5 minutes).

---

## Pagination
The news query endpoint supports limiting results via the `limit` parameter (1-100). Other endpoints do not currently support pagination.

---

## Interactive API Documentation
FastAPI provides automatic interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These interfaces allow you to explore all endpoints, test requests, and view schemas interactively.

---

## Environment Variables
The API behavior can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `DEBUG` | `true` | Enable debug mode |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `3306` | Database port |
| `DB_USER` | `root` | Database username |
| `DB_PASSWORD` | `""` | Database password |
| `DB_NAME` | `financial_agent` | Database name |
| `MILVUS_URI` | `http://localhost:19530` | Milvus vector database URI |
| `DEFAULT_LLM_MODEL` | `qwen-plus` | Default LLM model |
| `QWEN_CLOUD_MODEL` | `qwen-plus` | Cloud-based Qwen model |
| `OLLAMA_MODEL` | `qwen3.5:9b` | Local Ollama model |
| `FINNHUB_API_KEY` | `""` | Finnhub API key for market data |
| `DASHSCOPE_API_KEY` | `""` | DashScope API key for cloud LLM |

---

## Best Practices

### 1. Use Appropriate Analysis Windows
- **Short-term trends:** Use `days=7` for recent developments
- **Medium-term analysis:** Use `days=30` for monthly trends
- **Long-term analysis:** Use `days=90` or more for quarterly insights

### 2. Model Selection
- **Local Mode (`use_cloud=false`):** Faster, privacy-preserving, uses Ollama
- **Cloud Mode (`use_cloud=true`):** More powerful, requires API key, uses Qwen Plus

### 3. Error Handling
Always check the `success` field in responses and handle errors gracefully:

```javascript
const response = await fetch('/api/v1/analyze/company', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ticker: 'AAPL' })
});

const data = await response.json();
if (!data.success) {
  console.error('Analysis failed:', data.error);
  return;
}
// Process successful response
console.log('Analysis complete:', data.result);
```

### 4. Session Management
For chat conversations, maintain `session_id` across requests to preserve context:

```javascript
let sessionId = null;

async function chat(message) {
  const response = await api.post('/chat', {
    message,
    user_id: 'user123',
    session_id: sessionId
  });
  sessionId = response.session_id; // Save for next request
  return response;
}
```

---

## Support and Contact
For API issues or questions:
- Check the logs in `01_backend/logs/`
- Review the interactive documentation at `/docs`
- Refer to the architecture documentation in `15_docs/ARCHITECTURE.md`

---

## Changelog
### Version 1.0.0 (Current)
- Initial release
- Core endpoints: chat, company analysis, industry analysis, news query, watchlist
- Intent recognition system
- Quality evaluation framework
- Multi-dimensional analysis support