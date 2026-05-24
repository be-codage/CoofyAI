"""
Coofy AI - Pydantic Data Models & Schemas
=========================================
Defines all data structures used throughout the application.
"""

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field, validator
from typing import List, Optional


class ProductDeal(BaseModel):
    """Represents a single product deal analyzed by Coofy AI."""

    product_name: str = Field(default="Not Available", description="Full product name")
    product_url: Optional[str] = Field(default=None, description="Direct link to the product page")  # ← ADDED
    original_price: str = Field(default="Not Available", description="Original MRP price with currency")
    discounted_price: str = Field(default="Not Available", description="Sale/discounted price with currency")
    estimated_discount_percentage: float = Field(default=0.0, description="Calculated discount % (0-100)")
    deal_quality_rating: str = Field(
        default="Unknown",
        description="One of: HOT DEAL, GOOD DEAL, FAIR DEAL, RISKY DEAL, SUSPICIOUS"
    )
    trust_score: float = Field(default=0.0, ge=0, le=100, description="AI trust score 0-100")
    suspicious: bool = Field(default=False, description="True if suspicious pricing detected")
    reasons: str = Field(default="Not Available", description="Reasoning behind analysis")
    pros: str = Field(default="Not Available", description="Key advantages of this deal")
    cons: str = Field(default="Not Available", description="Key disadvantages or concerns")
    final_verdict: str = Field(default="Not Available", description="Buy Now / Consider Carefully / Avoid / Good Value")
    summary: str = Field(default="Not Available", description="One sentence summary")

    @validator("trust_score", pre=True)
    def clamp_trust_score(cls, v):
        try:
            return max(0.0, min(100.0, float(v)))
        except (TypeError, ValueError):
            return 0.0

    @validator("estimated_discount_percentage", pre=True)
    def clamp_discount(cls, v):
        try:
            return max(0.0, min(100.0, float(v)))
        except (TypeError, ValueError):
            return 0.0


class AnalysisResult(BaseModel):
    """Container for the full AI analysis result."""
    top_deals: List[ProductDeal] = Field(default=[], description="Ranked list of top deals")


class AnalyzeRequest(BaseModel):
    """Request body for analysis (if using POST)."""
    url: str = Field(..., description="Ecommerce URL to analyze")


class AnalyzeResponse(BaseModel):
    """Full API response from /analyze endpoint."""
    success: bool
    url: str
    platform: Optional[str] = "Unknown"
    page_type: Optional[str] = "Unknown"
    analysis_time_seconds: Optional[float] = None
    total_products_found: Optional[int] = 0
    top_deals: List[ProductDeal] = []
    error: Optional[str] = None


class BenchmarkResult(BaseModel):
    """Result of a single benchmark test."""
    url: str
    description: str
    status: str  # PASS, PARTIAL, FAIL, ERROR
    products_found: Optional[int] = 0
    elapsed_seconds: float
    platform: Optional[str] = None
    error: Optional[str] = None