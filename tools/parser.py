"""
Coofy AI - Content Parser & Platform Detector
===============================================
Parses scraped ecommerce content and detects the platform.
Provides utilities for cleaning and preparing content for AI analysis.
"""

import re
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger("coofy_ai.parser")


# Platform detection patterns
PLATFORM_PATTERNS = {
    "Amazon": ["amazon.in", "amazon.com", "amazon.co"],
    "Flipkart": ["flipkart.com"],
    "Myntra": ["myntra.com"],
    "Meesho": ["meesho.com"],
    "Ajio": ["ajio.com"],
    "Snapdeal": ["snapdeal.com"],
    "Nykaa": ["nykaa.com"],
    "JioMart": ["jiomart.com"],
    "Croma": ["croma.com"],
    "Tata CLiQ": ["tatacliq.com"],
}


def detect_platform(url: str) -> str:
    """
    Detect the ecommerce platform from the URL.

    Args:
        url: The ecommerce page URL

    Returns:
        Platform name string (e.g., 'Amazon', 'Flipkart')
    """
    try:
        domain = urlparse(url).netloc.lower()
        for platform, patterns in PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if pattern in domain:
                    logger.info(f"🏪 Platform detected: {platform}")
                    return platform
    except Exception as e:
        logger.warning(f"⚠️ Platform detection failed: {e}")

    logger.info("🏪 Platform: Unknown ecommerce site")
    return "Unknown"


def detect_page_type(url: str, content: str) -> str:
    """
    Determine if the page is a single product page or a multi-product listing page.

    Heuristics:
    - Listing pages typically have search queries, category paths, or 'search' / 'category' in URL
    - Single product pages have specific product identifiers like '/dp/', '/p/', '/product/'

    Args:
        url: The page URL
        content: Cleaned page text content

    Returns:
        'Single Product' or 'Multi-Product Listing'
    """
    url_lower = url.lower()

    # Single product URL indicators
    single_product_patterns = [
        r"/dp/",            # Amazon product page
        r"/p/\w+",          # Flipkart product
        r"/product/",       # Generic product
        r"/buy/",           # Myntra product
        r"/itm/",           # eBay item
    ]

    for pattern in single_product_patterns:
        if re.search(pattern, url_lower):
            logger.info("📦 Page type: Single Product")
            return "Single Product"

    # Listing page URL indicators
    listing_patterns = [
        r"/s\?",            # Amazon search
        r"/search",         # Generic search
        r"/category/",      # Category pages
        r"/promo/",         # Promo pages
        r"/deals",          # Deal pages
        r"/collection",     # Collection pages
        r"/shop/",          # Shop pages
        r"q=",              # Query parameter
        r"k=",              # Keyword parameter
    ]

    for pattern in listing_patterns:
        if re.search(pattern, url_lower):
            logger.info("📋 Page type: Multi-Product Listing")
            return "Multi-Product Listing"

    # Fallback: count price-like patterns in content to guess
    price_count = len(re.findall(r'₹[\d,]+|Rs\.?\s*[\d,]+|\$[\d,.]+', content))
    if price_count > 3:
        logger.info("📋 Page type: Multi-Product Listing (by content analysis)")
        return "Multi-Product Listing"

    logger.info("📦 Page type: Single Product (default)")
    return "Single Product"


def extract_price_signals(content: str) -> dict:
    """
    Extract raw pricing signals from content for additional context.

    Returns a dictionary with pricing statistics.
    """
    # Find all price-like values
    price_matches = re.findall(r'₹\s*([\d,]+)', content)
    prices = []
    for p in price_matches:
        try:
            val = float(p.replace(",", ""))
            if 10 <= val <= 10_000_000:  # Filter unreasonable values
                prices.append(val)
        except ValueError:
            continue

    if not prices:
        return {"price_count": 0}

    return {
        "price_count": len(prices),
        "min_price": min(prices),
        "max_price": max(prices),
        "avg_price": round(sum(prices) / len(prices), 2),
    }


def prepare_content_for_ai(url: str, content: str) -> dict:
    """
    Prepare a structured context package for AI analysis.

    Args:
        url: Original URL
        content: Cleaned page text

    Returns:
        Dictionary with platform, page_type, price_signals, and content
    """
    platform = detect_platform(url)
    page_type = detect_page_type(url, content)
    price_signals = extract_price_signals(content)

    context = {
        "url": url,
        "platform": platform,
        "page_type": page_type,
        "price_signals": price_signals,
        "content": content,
    }

    logger.info(
        f"📊 Content prepared — Platform: {platform}, "
        f"Type: {page_type}, Prices found: {price_signals.get('price_count', 0)}"
    )

    return context


# -------------------------------------------------------------------
# Quick test
# -------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    test_url = "https://www.amazon.in/s?k=laptops"
    test_content = "Laptop HP ₹45,999 ₹65,000 29% off\nLenovo ₹38,490 ₹55,000"
    result = prepare_content_for_ai(test_url, test_content)
    print(result)
