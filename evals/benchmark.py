"""
Coofy AI - Benchmark & Evaluation Suite
=========================================
Tests the full pipeline against known ecommerce URLs.
Measures scraping success, AI response quality, and end-to-end performance.
"""

import logging
import time
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.planner import PlannerAgent
from models.schemas import BenchmarkResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("coofy_ai.benchmark")


# ---------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------
TEST_CASES = [
    {
        "url": "https://www.amazon.in/s?k=laptops&ref=nb_sb_noss",
        "description": "Amazon India — Laptop listing page",
        "expected_type": "Multi-Product Listing",
    },
    {
        "url": "https://www.flipkart.com/search?q=smartphones&otracker=search",
        "description": "Flipkart — Smartphone search results",
        "expected_type": "Multi-Product Listing",
    },
    {
        "url": "https://www.amazon.in/s?k=headphones+under+2000",
        "description": "Amazon India — Budget headphones listing",
        "expected_type": "Multi-Product Listing",
    },
]


def run_benchmark():
    """
    Execute the full benchmark suite.
    Tests each URL through the complete pipeline and reports results.
    """
    logger.info("=" * 60)
    logger.info("🧪 COOFY AI BENCHMARK SUITE")
    logger.info("=" * 60)

    planner = PlannerAgent()
    results = []

    for i, test in enumerate(TEST_CASES, 1):
        url = test["url"]
        desc = test["description"]

        logger.info(f"\n{'─' * 50}")
        logger.info(f"🧪 Test {i}/{len(TEST_CASES)}: {desc}")
        logger.info(f"   URL: {url}")
        logger.info(f"{'─' * 50}")

        start = time.time()

        try:
            response = planner.analyze(url)
            elapsed = round(time.time() - start, 2)

            if response.success and response.top_deals:
                status = "PASS" if len(response.top_deals) >= 3 else "PARTIAL"
                products = len(response.top_deals)
            elif response.success:
                status = "PARTIAL"
                products = 0
            else:
                status = "FAIL"
                products = 0

            result = BenchmarkResult(
                url=url,
                description=desc,
                status=status,
                products_found=products,
                elapsed_seconds=elapsed,
                platform=response.platform,
                error=response.error,
            )

        except Exception as e:
            elapsed = round(time.time() - start, 2)
            result = BenchmarkResult(
                url=url,
                description=desc,
                status="ERROR",
                elapsed_seconds=elapsed,
                error=str(e),
            )

        results.append(result)

        icon = {"PASS": "✅", "PARTIAL": "🟡", "FAIL": "❌", "ERROR": "💥"}.get(result.status, "❓")
        logger.info(f"\n   {icon} Result: {result.status}")
        logger.info(f"   Products found: {result.products_found}")
        logger.info(f"   Time: {result.elapsed_seconds}s")
        if result.error:
            logger.info(f"   Error: {result.error}")

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    logger.info("\n" + "=" * 60)
    logger.info("📊 BENCHMARK SUMMARY")
    logger.info("=" * 60)

    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    partial = sum(1 for r in results if r.status == "PARTIAL")
    failed = sum(1 for r in results if r.status in ("FAIL", "ERROR"))
    avg_time = sum(r.elapsed_seconds for r in results) / total if total else 0

    logger.info(f"   Total Tests:    {total}")
    logger.info(f"   ✅ Passed:      {passed}")
    logger.info(f"   🟡 Partial:     {partial}")
    logger.info(f"   ❌ Failed:      {failed}")
    logger.info(f"   ⏱️  Avg Time:    {avg_time:.1f}s")
    logger.info(f"   Score:          {passed}/{total} ({passed/total*100:.0f}%)")

    # Save results to JSON
    output = {
        "summary": {
            "total": total,
            "passed": passed,
            "partial": partial,
            "failed": failed,
            "avg_time_seconds": round(avg_time, 2),
        },
        "results": [r.model_dump() for r in results],
    }

    output_file = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    logger.info(f"\n💾 Results saved to: {output_file}")

    return results


if __name__ == "__main__":
    run_benchmark()
