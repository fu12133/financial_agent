"""
API route definitions
"""
import sys
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException
from loguru import logger

from models.schemas import (
    ChatRequest, ChatResponse,
    CompanyAnalysisRequest, CompanyAnalysisResponse,
    IndustryAnalysisRequest, IndustryAnalysisResponse,
    NewsQueryRequest, NewsResponse,
    WatchlistRequest, WatchlistResponse
)
from services.agent_service import AgentService
from services.news_service import NewsService

router = APIRouter()

agent_service = AgentService()
news_service = NewsService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request: user={request.user_id}, message={request.message[:50]}")

        result = await agent_service.chat(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/company", response_model=CompanyAnalysisResponse)
async def analyze_company(request: CompanyAnalysisRequest):
    try:
        logger.info(f"Received company analysis request: ticker={request.ticker}")

        result = await agent_service.analyze_company(
            ticker=request.ticker,
            company_name=request.company_name,
            days=request.days,
            use_cloud=request.use_cloud
        )

        return CompanyAnalysisResponse(**result)

    except Exception as e:
        logger.error(f"Company analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/industry", response_model=IndustryAnalysisResponse)
async def analyze_industry(request: IndustryAnalysisRequest):
    try:
        logger.info(f"Received industry analysis request: industry={request.industry}")

        result = await agent_service.analyze_industry(
            industry=request.industry,
            industry_name=request.industry_name,
            days=request.days,
            use_cloud=request.use_cloud
        )

        return IndustryAnalysisResponse(**result)

    except Exception as e:
        logger.error(f"Industry analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/news/query", response_model=NewsResponse)
async def query_news(request: NewsQueryRequest):
    try:
        logger.info(f"Received news query request: ticker={request.ticker}")

        result = await news_service.query_news(
            ticker=request.ticker,
            days=request.days,
            limit=request.limit
        )

        return NewsResponse(**result)

    except Exception as e:
        logger.error(f"News query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watchlist", response_model=WatchlistResponse)
async def manage_watchlist(request: WatchlistRequest):
    try:
        logger.info(f"Received watchlist request: action={request.action}")

        result = await agent_service.manage_watchlist(
            action=request.action,
            ticker=request.ticker,
            company_name=request.company_name
        )

        return WatchlistResponse(**result)

    except Exception as e:
        logger.error(f"Watchlist operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist/{user_id}")
async def get_watchlist(user_id: str = "default"):
    try:
        watchlist = await agent_service.get_watchlist(user_id)
        return {
            "success": True,
            "user_id": user_id,
            "watchlist": watchlist,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))
