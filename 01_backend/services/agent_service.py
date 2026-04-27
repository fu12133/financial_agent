"""
Agent Service Layer
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from datetime import datetime

# Add project root directory to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Use importlib to import modules starting with numbers
import importlib
agent_module = importlib.import_module('03_agent.agent_core')
FinancialAgent = agent_module.FinancialAgent


class AgentService:
    _instance = None
    _agents: Dict[str, FinancialAgent] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_agent(self, user_id: str = "default") -> FinancialAgent:
        if user_id not in self._agents:
            logger.info(f"Creating new Agent: user_id={user_id}")
            agent = FinancialAgent(
                user_id=user_id,
                verbose=False
            )
            # Initialize Agent immediately
            agent.initialize()
            self._agents[user_id] = agent
        return self._agents[user_id]

    async def chat(self, message: str, user_id: str = "default",
                   session_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            agent = self._get_agent(user_id)

            if session_id:
                agent.session_id = session_id

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: agent.chat(message)
            )

            logger.info(f"Chat success: user={user_id}")
            return result

        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": {"message": "Processing failed", "type": "error"},
                "timestamp": datetime.now().isoformat()
            }

    async def analyze_company(self, ticker: str, company_name: Optional[str] = None,
                             days: int = 7, use_cloud: Optional[bool] = None) -> Dict[str, Any]:
        try:
            agent = self._get_agent()

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: agent.analyze_company(
                    ticker=ticker,
                    company_name=company_name or ticker,
                    days=days
                )
            )

            logger.info(f"Company analysis success: ticker={ticker}")

            report_path = None
            if result.get('success') and result.get('result'):
                report_path = result['result'].get('report_path')

            return {
                "success": result.get('success', False),
                "ticker": ticker,
                "company_name": company_name or ticker,
                "result": result.get('result'),
                "report_path": report_path,
                "timestamp": datetime.now().isoformat(),
                "error": result.get('error') if not result.get('success') else None
            }

        except Exception as e:
            logger.error(f"Company analysis failed: {e}")
            return {
                "success": False,
                "ticker": ticker,
                "company_name": company_name or ticker,
                "result": None,
                "report_path": None,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    async def analyze_industry(self, industry: str, industry_name: Optional[str] = None,
                              days: int = 7, use_cloud: Optional[bool] = None) -> Dict[str, Any]:
        try:
            agent = self._get_agent()

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: agent.analyze_industry(
                    industry=industry,
                    industry_name=industry_name or industry,
                    days=days
                )
            )

            logger.info(f"Industry analysis success: industry={industry}")

            report_path = None
            if result.get('success') and result.get('result'):
                # Extract report path from result (if any)
                report_data = result['result']
                if isinstance(report_data, dict):
                    report_path = report_data.get('report_path')

            return {
                "success": result.get('success', False),
                "industry": industry,
                "industry_name": industry_name or industry,
                "result": result.get('result'),
                "report_path": report_path,
                "timestamp": datetime.now().isoformat(),
                "error": result.get('error') if not result.get('success') else None
            }

        except Exception as e:
            logger.error(f"Industry analysis failed: {e}")
            return {
                "success": False,
                "industry": industry,
                "industry_name": industry_name or industry,
                "result": None,
                "report_path": None,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    async def manage_watchlist(self, action: str, ticker: Optional[str] = None,
                              company_name: Optional[str] = None) -> Dict[str, Any]:
        try:
            agent = self._get_agent()
            
            logger.info(f"Debug - Agent type: {type(agent)}")
            logger.info(f"Debug - Agent has memory attribute: {hasattr(agent, 'memory')}")
            
            if hasattr(agent, 'memory'):
                logger.info(f"Debug - memory type: {type(agent.memory)}")

            if action == "view":
                watchlist = agent.memory.get_watchlist()
                
                logger.info(f"Debug - watchlist type: {type(watchlist)}, value: {watchlist}")
                
                if not isinstance(watchlist, list):
                    logger.warning(f"⚠️  get_watchlist did not return a list: {type(watchlist)}")
                    watchlist = []
                
                return {
                    "success": True,
                    "action": action,
                    "watchlist": watchlist,
                    "message": f"Current watchlist: {', '.join(watchlist) if watchlist else 'Empty'}",
                    "timestamp": datetime.now().isoformat()
                }

            elif action == "add":
                if not ticker:
                    raise ValueError("Adding stock requires ticker")

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: agent.memory.add_to_watchlist(ticker, company_name or "")
                )
                
                logger.info(f"Debug - add_to_watchlist return value: {result}, type: {type(result)}")

                return {
                    "success": True,
                    "action": action,
                    "message": f"Added {company_name or ticker} to watchlist",
                    "timestamp": datetime.now().isoformat()
                }

            elif action == "remove":
                return {
                    "success": False,
                    "action": action,
                    "message": "Remove feature not yet implemented",
                    "timestamp": datetime.now().isoformat()
                }

            else:
                raise ValueError(f"Unknown operation: {action}")

        except Exception as e:
            logger.error(f"Watchlist operation failed: {e}", exc_info=True)
            return {
                "success": False,
                "action": action,
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
