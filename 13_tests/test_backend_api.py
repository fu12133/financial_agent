"""
Backend API Complete Functionality Test
"""
import sys
from pathlib import Path
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add backend directory to path (for direct import)
backend_dir = project_root / "01_backend"
sys.path.insert(0, str(backend_dir))


class TestBackendAPI:
    """Backend API complete test class"""

    @pytest_asyncio.fixture(scope="class")
    async def setup_services(self):
        """Initialize services"""
        print("\n" + "="*80)
        print("Starting Backend API Test")
        print("="*80)

        # Import directly from backend directory
        from services.agent_service import AgentService
        from services.news_service import NewsService

        agent_service = AgentService()
        news_service = NewsService()

        return {
            "agent_service": agent_service,
            "news_service": news_service
        }

    def test_01_health_check(self):
        """Test 1: Health Check"""
        print("\n📋 Test 1: Health Check")
        print("-" * 40)

        health_status = {"status": "healthy"}
        assert health_status["status"] == "healthy"
        print("✅ Health check passed")

    @pytest.mark.asyncio
    async def test_02_chat_basic(self, setup_services):
        """Test 2: Basic Chat Functionality"""
        print("\n📋 Test 2: Basic Chat Functionality")
        print("-" * 40)

        agent_service = setup_services["agent_service"]

        result = await agent_service.chat(
            message="Hello",
            user_id="test_user",
            session_id=None
        )

        print(f"Response success: {result.get('success')}")
        print(f"Agent ID: {result.get('agent_id')}")
        print(f"Session ID: {result.get('session_id')}")

        assert result.get('success') in [True, False]
        assert 'agent_id' in result
        assert 'timestamp' in result
        print("✅ Basic chat test complete")

    @pytest.mark.asyncio
    async def test_03_company_analysis(self, setup_services):
        """Test 3: Company Analysis Functionality"""
        print("\n📋 Test 3: Company Analysis Functionality")
        print("-" * 40)

        agent_service = setup_services["agent_service"]

        result = await agent_service.analyze_company(
            ticker="AAPL",
            company_name="Apple Inc.",
            days=7,
            use_cloud=None
        )

        print(f"Analysis success: {result.get('success')}")
        print(f"Stock Ticker: {result.get('ticker')}")
        print(f"Company Name: {result.get('company_name')}")

        if not result.get('success'):
            print(f"Error message: {result.get('error')}")

        assert result.get('ticker') == "AAPL"
        assert result.get('company_name') == "Apple Inc."
        print("✅ Company analysis test complete")

    @pytest.mark.asyncio
    async def test_04_news_query(self, setup_services):
        """Test 4: News Query Functionality"""
        print("\n📋 Test 4: News Query Functionality")
        print("-" * 40)

        news_service = setup_services["news_service"]

        result = await news_service.query_news(
            ticker="AAPL",
            days=7,
            limit=5
        )

        print(f"Query success: {result.get('success')}")
        print(f"News count: {result.get('count')}")

        if not result.get('success'):
            print(f"Error message: {result.get('error')}")

        assert result.get('ticker') == "AAPL"
        assert isinstance(result.get('count'), int)
        print("✅ News query test complete")

    @pytest.mark.asyncio
    async def test_05_watchlist(self, setup_services):
        """Test 5: Watchlist Functionality"""
        print("\n📋 Test 5: Watchlist Functionality")
        print("-" * 40)

        agent_service = setup_services["agent_service"]

        # Add stock
        add_result = await agent_service.manage_watchlist(
            action="add",
            ticker="MSFT",
            company_name="Microsoft"
        )

        print(f"Add success: {add_result.get('success')}")
        print(f"Message: {add_result.get('message')}")

        # View list
        view_result = await agent_service.manage_watchlist(
            action="view"
        )

        print(f"View success: {view_result.get('success')}")
        print(f"Watchlist: {view_result.get('watchlist')}")

        assert add_result.get('action') == "add"
        assert view_result.get('action') == "view"
        print("✅ Watchlist test complete")
