"""
Coofy AI - FastAPI Backend
===========================
RESTful API backend that exposes the /analyze endpoint.
Receives ecommerce URLs, runs the full analysis pipeline, and returns structured JSON.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from agents.planner import PlannerAgent
from models.schemas import AnalyzeResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("coofy_ai.api")


# ---------------------------------------------------------------
# App Lifespan — Initialize planner agent once at startup
# ---------------------------------------------------------------
planner: PlannerAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources at startup, clean up at shutdown."""
    global planner
    logger.info("🚀 Coofy AI Backend starting up...")
    planner = PlannerAgent()
    logger.info("✅ Planner agent initialized")
    yield
    logger.info("👋 Coofy AI Backend shutting down...")


# ---------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------
app = FastAPI(
    title="Coofy AI — Ecommerce Deal Intelligence",
    description=(
        "Advanced AI-powered ecommerce deal intelligence platform. "
        "Analyzes product pages, detects fake discounts, ranks deals, "
        "and provides trust scoring."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root():
    """Root health check endpoint."""
    return {
        "status": "online",
        "service": "Coofy AI",
        "version": "1.0.0",
        "message": "🧠 Coofy AI Deal Intelligence Engine is running!",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "Coofy AI Backend",
        "planner_ready": planner is not None,
    }


# ---------------------------------------------------------------
# Main Analysis Endpoint
# ---------------------------------------------------------------
@app.get("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_url(
    url: str = Query(
        ...,
        description="Ecommerce URL to analyze (e.g., Amazon/Flipkart product or listing page)",
        examples=["https://www.amazon.in/s?k=laptops"],
    )
):
    """
    Analyze an ecommerce URL for deals, pricing intelligence, and fraud detection.

    The analysis pipeline:
    1. Scrapes the page using Selenium (handles JS-rendered content)
    2. Parses and cleans the content
    3. Sends to AI for deep deal analysis
    4. Returns ranked deals with trust scores

    Query Parameters:
        url: The ecommerce page URL to analyze

    Returns:
        AnalyzeResponse with ranked deals, trust scores, and AI insights
    """
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="URL parameter is required")

    logger.info(f"📥 Analysis request received: {url}")

    try:
        result = planner.analyze(url)
        return result

    except Exception as e:
        logger.error(f"❌ Unhandled error in /analyze: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ---------------------------------------------------------------
# Run with: uvicorn app.api:app --reload
# ---------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
