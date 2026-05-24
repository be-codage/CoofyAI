"""
Coofy AI - Planner Agent
=========================
Orchestrates the full analysis pipeline:
URL → Scrape → Parse → AI Analysis → Structured Result

Acts as the central coordinator between all system components.
"""

import logging
import time
from typing import Optional

from tools.scraper import EcommerceScraper
from tools.parser import prepare_content_for_ai
from agents.validator import DealValidator
from models.schemas import AnalyzeResponse, ProductDeal

logger = logging.getLogger("coofy_ai.planner")


class PlannerAgent:
    """
    Central orchestrator for the Coofy AI analysis pipeline.

    Responsibilities:
    1. Validate the incoming URL
    2. Invoke the Selenium scraper
    3. Parse and prepare content
    4. Send to AI validator for deal analysis
    5. Return structured response
    """

    def __init__(self):
        """Initialize the planner with scraper and validator instances."""
        self.scraper = EcommerceScraper()
        self.validator = DealValidator()

    def _validate_url(self, url: str) -> str:
        """
        Basic URL validation and normalization.
        Ensures the URL has a proper scheme.
        """
        url = url.strip()
        if not url:
            raise ValueError("URL cannot be empty")

        # Add https:// if no scheme provided
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        return url

    def analyze(self, url: str) -> AnalyzeResponse:
        """
        Run the complete analysis pipeline on the given URL.

        Pipeline:
        1. Validate URL
        2. Scrape page with Selenium
        3. Parse content and detect platform
        4. Send to AI for deal analysis
        5. Return structured results

        Args:
            url: Ecommerce page URL to analyze

        Returns:
            AnalyzeResponse with ranked deals or error information
        """
        start_time = time.time()

        logger.info("=" * 60)
        logger.info(f"🧠 COOFY AI — Starting analysis for: {url}")
        logger.info("=" * 60)

        try:
            # Step 1: Validate URL
            url = self._validate_url(url)
            logger.info(f"✅ Step 1/4 — URL validated: {url}")

            # Step 2: Scrape the page
            logger.info("🔄 Step 2/4 — Launching scraper...")
            page_content = self.scraper.scrape(url)
            logger.info(f"✅ Step 2/4 — Scraped {len(page_content)} characters")

            # Step 3: Parse and prepare content
            logger.info("🔄 Step 3/4 — Parsing content...")
            context = prepare_content_for_ai(url, page_content)
            logger.info(f"✅ Step 3/4 — Content parsed ({context['platform']}, {context['page_type']})")

            # Step 4: AI Analysis
            logger.info("🔄 Step 4/4 — Running AI deal analysis...")
            analysis_result = self.validator.analyze_deals(context)
            logger.info(f"✅ Step 4/4 — AI analysis complete, {len(analysis_result.top_deals)} deals found")

            elapsed = round(time.time() - start_time, 2)

            response = AnalyzeResponse(
                success=True,
                url=url,
                platform=context["platform"],
                page_type=context["page_type"],
                analysis_time_seconds=elapsed,
                total_products_found=len(analysis_result.top_deals),
                top_deals=analysis_result.top_deals,
                error=None,
            )

            logger.info(f"🎉 Analysis complete in {elapsed}s — {len(analysis_result.top_deals)} top deals")
            return response

        except ValueError as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"❌ Validation error: {e}")
            return AnalyzeResponse(
                success=False,
                url=url,
                analysis_time_seconds=elapsed,
                error=f"Invalid input: {str(e)}",
            )

        except RuntimeError as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"❌ Runtime error: {e}")
            return AnalyzeResponse(
                success=False,
                url=url,
                analysis_time_seconds=elapsed,
                error=f"Processing error: {str(e)}",
            )

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"❌ Unexpected error: {e}")
            return AnalyzeResponse(
                success=False,
                url=url,
                analysis_time_seconds=elapsed,
                error=f"Unexpected error: {str(e)}",
            )


# -------------------------------------------------------------------
# Quick test
# -------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    planner = PlannerAgent()
    result = planner.analyze("https://www.amazon.in/s?k=laptops")
    print(result.model_dump_json(indent=2))
