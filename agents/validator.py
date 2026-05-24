"""
Coofy AI - Deal Validator Agent (AI-Powered)
=============================================
Uses Groq API with llama-3.3-70b-versatile to analyze ecommerce deals.
Acts as a pricing intelligence engine, fraud detector, and deal ranker.
"""

import os
import re
import json
import logging
from typing import Optional

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from groq import Groq

from models.schemas import AnalysisResult, ProductDeal

# Load environment variables from .env
load_dotenv(override=True)

logger = logging.getLogger("coofy_ai.validator")


class DealValidator:
    """
    AI-powered deal analysis engine using Groq's LLM.

    Responsibilities:
    - Analyze products for deal quality
    - Detect fake discounts and scams
    - Score trustworthiness
    - Rank deals from BEST to WORST
    - Return structured JSON results
    """

    # The AI model to use
    MODEL = "llama-3.3-70b-versatile"

    # Max tokens for response
    MAX_TOKENS = 4096

    # Temperature for consistent analysis
    TEMPERATURE = 0.1

    def __init__(self):
        """Initialize the Groq client with API key from environment."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise ValueError(
                "❌ GROQ_API_KEY not found! "
                "Please set it in the .env file. "
                "Get a free key at: https://console.groq.com/keys"
            )
        self.client = Groq(api_key=api_key)
        logger.info("✅ Groq client initialized")

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that defines the AI's behavior.
        This is critical for consistent, high-quality analysis.
        """
        return """You are Coofy AI, an advanced ecommerce deal intelligence system.

You are an expert in:
- Ecommerce pricing analysis
- Fake discount detection
- Scam pattern recognition
- Trust scoring
- Deal quality ranking

YOUR TASK:
Analyze ALL products found on the ecommerce page and return a ranked list of the TOP 5 BEST deals.

ANALYSIS REQUIREMENTS:

1. DETECT all products on the page
2. EXTRACT for each product:
   - Product name (full name)
   - Product URL (direct link to the product page — extract from href attributes or construct from base URL + product path)
   - Original price (MRP/list price with currency symbol)
   - Discounted price (sale price with currency symbol)
   - Estimated discount percentage

3. ANALYZE for each product:
   - Is the discount REAL or FAKE?
   - Are there suspicious pricing patterns? (inflated MRP, unrealistic discounts, etc.)
   - Is there urgency manipulation? (limited time, only X left, etc.)
   - Any scam indicators?

4. SCORE trustworthiness (0-100):
   - 80-100: Very trustworthy, genuine deal
   - 60-79: Mostly trustworthy, minor concerns
   - 40-59: Questionable, proceed with caution
   - 0-39: Suspicious, likely fake or scam

5. RATE deal quality:
   - "HOT DEAL" — exceptional value, genuine high discount
   - "GOOD DEAL" — solid value, real savings
   - "FAIR DEAL" — average, moderate savings
   - "RISKY DEAL" — questionable discount or pricing
   - "SUSPICIOUS" — likely fake or manipulative

6. RANK all products from BEST to WORST deal
7. Return only the TOP 5 deals

CRITICAL RULES:
- Return ONLY valid JSON, no markdown formatting, no code blocks
- Do NOT hallucinate product names or prices
- Use "Not Available" for any missing data
- For product_url: extract real href links from the page content; if not found use null
- Be skeptical of discounts above 70%
- Consider the product category when evaluating deals
- Provide specific, actionable reasons for your analysis
"""

    def _build_user_prompt(self, context: dict) -> str:
        """
        Build the user prompt with the actual page content and context.
        """
        platform = context.get("platform", "Unknown")
        page_type = context.get("page_type", "Unknown")
        price_signals = context.get("price_signals", {})
        content = context.get("content", "")
        base_url = context.get("url", "")  # ← used as fallback for product_url

        return f"""Analyze this ecommerce page and find the TOP 5 BEST deals.

PLATFORM: {platform}
PAGE TYPE: {page_type}
BASE URL: {base_url}
PRICE SIGNALS: {json.dumps(price_signals)}

PAGE CONTENT:
{content}

RESPOND with ONLY this JSON structure (no markdown, no backticks, no explanation):

{{
  "top_deals": [
    {{
      "product_name": "Full product name",
      "product_url": "https://full-direct-link-to-product-page-or-null",
      "original_price": "₹XX,XXX or $XX.XX",
      "discounted_price": "₹XX,XXX or $XX.XX",
      "estimated_discount_percentage": 25,
      "deal_quality_rating": "HOT DEAL | GOOD DEAL | FAIR DEAL | RISKY DEAL | SUSPICIOUS",
      "trust_score": 85,
      "suspicious": false,
      "reasons": "Detailed reasoning for the analysis",
      "pros": "Key advantages of this deal",
      "cons": "Key concerns or disadvantages",
      "final_verdict": "Buy Now | Good Value | Consider Carefully | Avoid",
      "summary": "One sentence summary of this deal"
    }}
  ]
}}

For product_url: extract the direct product link from href attributes in the page content.
If the link is relative (e.g. /dp/B123), prepend the base domain from BASE URL above.
If no link found at all, use null.

Return UP TO 5 deals, ranked from BEST to WORST.
Return ONLY valid JSON. No markdown. No explanation. No backticks."""

    def _parse_ai_response(self, raw_response: str) -> AnalysisResult:
        """
        Robustly parse the AI response into structured data.

        Handles:
        - Clean JSON
        - JSON wrapped in markdown code blocks
        - Minor formatting issues
        - Malformed JSON with recovery attempts
        """
        logger.info("🔍 Parsing AI response...")

        # Step 1: Try direct JSON parsing
        try:
            data = json.loads(raw_response)
            logger.info("✅ Direct JSON parse successful")
            return self._validate_result(data)
        except json.JSONDecodeError:
            pass

        # Step 2: Remove markdown code blocks (```json ... ```)
        cleaned = raw_response
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            logger.info("✅ Markdown-cleaned JSON parse successful")
            return self._validate_result(data)
        except json.JSONDecodeError:
            pass

        # Step 3: Extract JSON from anywhere in the response using regex
        json_pattern = r'\{[\s\S]*"top_deals"[\s\S]*\}'
        match = re.search(json_pattern, raw_response)
        if match:
            try:
                data = json.loads(match.group())
                logger.info("✅ Regex-extracted JSON parse successful")
                return self._validate_result(data)
            except json.JSONDecodeError:
                pass

        # Step 4: Try to find JSON array pattern
        array_pattern = r'\[[\s\S]*\{[\s\S]*"product_name"[\s\S]*\}[\s\S]*\]'
        match = re.search(array_pattern, raw_response)
        if match:
            try:
                deals_list = json.loads(match.group())
                data = {"top_deals": deals_list}
                logger.info("✅ Array-extracted JSON parse successful")
                return self._validate_result(data)
            except json.JSONDecodeError:
                pass

        # Step 5: Fallback — return empty result with error context
        logger.error("❌ All JSON parsing attempts failed")
        logger.error(f"Raw response preview: {raw_response[:500]}")

        return AnalysisResult(
            top_deals=[
                ProductDeal(
                    product_name="⚠️ AI Parsing Error",
                    summary="The AI response could not be parsed. Try again or use a different URL.",
                    reasons="The AI model returned a response in an unexpected format.",
                    trust_score=0,
                    deal_quality_rating="SUSPICIOUS",
                )
            ]
        )

    def _validate_result(self, data: dict) -> AnalysisResult:
        """
        Validate and convert raw dict to AnalysisResult with Pydantic models.
        Handles missing fields gracefully.
        """
        if "top_deals" not in data:
            data = {"top_deals": [data] if isinstance(data, dict) else []}

        deals = []
        for item in data["top_deals"][:5]:  # Cap at 5
            try:
                deal = ProductDeal(**item)
                deals.append(deal)
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse deal item: {e}")
                continue

        logger.info(f"✅ Validated {len(deals)} deals")
        return AnalysisResult(top_deals=deals)

    def analyze_deals(self, context: dict) -> AnalysisResult:
        """
        Send content to Groq AI for deal analysis.

        Args:
            context: Dictionary with url, platform, page_type, price_signals, content

        Returns:
            AnalysisResult with ranked ProductDeal list
        """
        logger.info(f"🤖 Sending to Groq AI ({self.MODEL})...")

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": self._build_user_prompt(context)},
                ],
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )

            raw_response = response.choices[0].message.content
            logger.info(f"✅ Groq AI responded ({len(raw_response)} chars)")

            return self._parse_ai_response(raw_response)

        except Exception as e:
            logger.error(f"❌ Groq API error: {e}")
            return AnalysisResult(
                top_deals=[
                    ProductDeal(
                        product_name="⚠️ AI API Error",
                        summary=f"AI analysis failed: {str(e)}",
                        reasons=str(e),
                        trust_score=0,
                        deal_quality_rating="SUSPICIOUS",
                    )
                ]
            )


# -------------------------------------------------------------------
# Quick test
# -------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    validator = DealValidator()
    test_context = {
        "url": "https://example.com",
        "platform": "Amazon",
        "page_type": "Multi-Product Listing",
        "price_signals": {"price_count": 3, "min_price": 999, "max_price": 45999},
        "content": "HP Laptop 15s ₹45,999 MRP ₹65,000 29% off | Lenovo IdeaPad ₹38,490 MRP ₹55,000 30% off",
    }
    result = validator.analyze_deals(test_context)
    print(json.dumps(result.model_dump(), indent=2))