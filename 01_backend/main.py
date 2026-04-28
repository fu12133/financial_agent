"""
FastAPI Main Application Entry Point
"""
import sys
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# Use importlib to import modules starting with numbers
import importlib
api_module = importlib.import_module('01_backend.api.routes')
core_module = importlib.import_module('01_backend.core.config')

router = api_module.router
settings = core_module.settings

# Configure loguru logging
logger.remove()  # Remove default handler

# Add file handler (always keep detailed logs in file)
logger.add("logs/backend_{time}.log", rotation="1 day", retention="7 days", level="DEBUG")

# Filter function to suppress verbose INFO logs from specific modules
def log_filter(record):
    """Filter out verbose INFO logs from internal modules"""
    if settings.DEBUG:
        # In debug mode, show everything except very verbose modules
        verbose_modules = [
            '08_pipeline.embedding',
            '10_storage.milvus_manager', 
            '09_retrieve.rag_service',
            '09_retrieve.rag_searcher',
            '09_retrieve.llm_client',
        ]
        record_module = record['name']
        # If it's an INFO log from a verbose module, suppress it
        if record['level'].name == 'INFO' and any(record_module.startswith(mod) for mod in verbose_modules):
            return False
    return True

# Add console handler with filter
if settings.DEBUG:
    logger.add(sys.stderr, level="DEBUG", filter=log_filter, 
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
else:
    logger.add(sys.stderr, level="WARNING", 
               format="<level>{level: <8}</level> | <level>{message}</level>")

app = FastAPI(
    title="Financial Agent API",
    description="Financial Agent API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Financial Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
