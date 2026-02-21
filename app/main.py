from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import receipts, templates, health
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Receipt Service starting up...")
    yield
    logger.info("Receipt Service shutting down...")


app = FastAPI(
    title="Restaurant Receipt Service",
    description="Receipt generation and printing service for thermal printers",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(receipts.router, prefix="/api/v1/receipts", tags=["Receipts"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["Templates"])


@app.get("/")
async def root():
    return {
        "service": "Restaurant Receipt Service",
        "version": "1.0.0",
        "status": "running"
    }
