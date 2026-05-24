"""
Coofy AI - Ecommerce Web Scraper
=================================
Uses Selenium + BeautifulSoup to scrape dynamic ecommerce pages.
Supports JavaScript-rendered content, lazy-loaded products, and dynamic pricing.
"""

import logging
import time
import re
from typing import Optional
from urllib.parse import urljoin, urlparse  # ← ADDED
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# pyrefly: ignore [missing-import]
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logger = logging.getLogger("coofy_ai.scraper")


class EcommerceScraper:
    """
    Production-grade ecommerce scraper that handles:
    - JavaScript-rendered pages (React, Angular, etc.)
    - Lazy-loaded product listings
    - Dynamic pricing sections
    - Anti-bot headers and user-agent spoofing
    """

    # Common user agent string to mimic real browser
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    # Maximum page load wait time in seconds
    PAGE_LOAD_TIMEOUT = 30

    # Number of scroll iterations to trigger lazy-loading
    SCROLL_ITERATIONS = 5

    # Pause between scrolls (seconds)
    SCROLL_PAUSE = 1.5

    def __init__(self):
        """Initialize scraper with default configuration."""
        self.driver: Optional[webdriver.Chrome] = None

    def _build_chrome_options(self) -> Options:
        """
        Build Chrome options optimized for headless scraping.
        Includes anti-detection measures and performance flags.
        """
        options = Options()

        # Run in headless mode (no visible browser window)
        options.add_argument("--headless=new")

        # Anti-detection and stability flags
        options.add_argument(f"--user-agent={self.USER_AGENT}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--log-level=3")  # Suppress console logs

        # Performance optimizations
        options.add_argument("--disable-images")  # Faster load
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        return options

    def _launch_browser(self) -> webdriver.Chrome:
        """
        Launch headless Chrome browser with auto-installed ChromeDriver.
        Uses webdriver-manager for automatic driver management.
        """
        logger.info("🚀 Launching headless Chrome browser...")

        options = self._build_chrome_options()

        try:
            # Auto-install matching ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)

            # Remove webdriver detection flag
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            logger.info("✅ Chrome browser launched successfully")
            return driver

        except Exception as e:
            logger.error(f"❌ Failed to launch Chrome: {e}")
            raise RuntimeError(f"Browser launch failed: {e}")

    def _scroll_page(self, driver: webdriver.Chrome) -> None:
        """
        Scroll the page multiple times to trigger lazy-loading of products.
        Many ecommerce sites load products as user scrolls down.
        """
        logger.info(f"📜 Scrolling page ({self.SCROLL_ITERATIONS} iterations)...")

        for i in range(self.SCROLL_ITERATIONS):
            # Scroll to bottom of current viewport
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.SCROLL_PAUSE)

            # Also try scrolling by a fixed amount for partial lazy-load triggers
            driver.execute_script(f"window.scrollBy(0, {800 * (i + 1)});")
            time.sleep(0.5)

        # Scroll back to top for consistent state
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

        logger.info("✅ Page scrolling complete")

    def _wait_for_content(self, driver: webdriver.Chrome) -> None:
        """
        Wait for the page body to be present and main content to render.
        Uses explicit waits instead of arbitrary sleeps.
        """
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Additional wait for common ecommerce product containers
            product_selectors = [
                "[data-component-type='s-search-result']",   # Amazon
                "._1AtVbE",                                    # Flipkart
                ".product-base",                               # Myntra
                ".product-card",                               # Generic
                ".s-result-item",                              # Amazon alt
                "[data-id]",                                   # Generic product
            ]

            for selector in product_selectors:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ Found product container: {selector}")
                    break
                except Exception:
                    continue

        except Exception as e:
            logger.warning(f"⚠️ Content wait timeout: {e}")

    def _extract_html(self, driver: webdriver.Chrome) -> str:
        """Extract the full rendered HTML from the page."""
        return driver.page_source

    # ── ADDED ──────────────────────────────────────────────────────────────────
    def _extract_product_links(self, raw_html: str, base_url: str) -> str:
        """
        Extract product href links from the page and inject them as structured
        text so the AI can pick them up as product_url values.

        Targets anchor tags that look like product detail page links:
        - Amazon:   /dp/ASIN
        - Flipkart: /p/ or productid
        - Myntra:   /buy/
        - Generic:  /product/ or /item/ or /detail/

        Returns a compact block of "PRODUCT_LINK: <url>" lines to append
        to the cleaned content.
        """
        logger.info("🔗 Extracting product links from page...")

        soup = BeautifulSoup(raw_html, "html.parser")

        # Patterns that strongly indicate a product detail page link
        product_path_patterns = re.compile(
            r'(/dp/[A-Z0-9]{10}'           # Amazon ASIN
            r'|/p/[a-z0-9]+)'              # Flipkart product
            r'|/buy/'                       # Myntra
            r'|/product/'                   # Generic
            r'|/item/'                      # Generic
            r'|/detail/'                    # Generic
            r'|productid=[0-9]+'            # Query-param style
            r'|pid=[0-9A-Za-z]+',           # Flipkart pid
            re.IGNORECASE,
        )

        seen = set()
        link_lines = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()

            # Skip empty, javascript, anchor, or mailto links
            if not href or href.startswith(("#", "javascript", "mailto")):
                continue

            # Resolve relative URLs to absolute using the base page URL
            full_url = urljoin(base_url, href)

            # Only keep links on the same domain (avoid external ad links)
            base_domain = urlparse(base_url).netloc
            link_domain = urlparse(full_url).netloc
            if base_domain not in link_domain:
                continue

            # Only keep links that match product page patterns
            if not product_path_patterns.search(full_url):
                continue

            # Deduplicate
            if full_url in seen:
                continue
            seen.add(full_url)

            link_lines.append(f"PRODUCT_LINK: {full_url}")

        logger.info(f"✅ Extracted {len(link_lines)} product links")

        if link_lines:
            return "\n\n--- PRODUCT LINKS FOUND ON PAGE ---\n" + "\n".join(link_lines[:30])
        return ""
    # ───────────────────────────────────────────────────────────────────────────

    def _clean_html(self, raw_html: str) -> str:
        """
        Clean and extract meaningful text content from HTML.
        Removes scripts, styles, nav, footers and other noise.
        Returns clean text suitable for AI analysis.
        """
        logger.info("🧹 Cleaning HTML content...")

        soup = BeautifulSoup(raw_html, "html.parser")

        # Remove non-content elements
        tags_to_remove = [
            "script", "style", "noscript", "iframe", "svg",
            "header", "footer", "nav", "aside", "form",
            "meta", "link", "button", "input",
        ]
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()

        # Extract text with reasonable spacing
        text = soup.get_text(separator="\n", strip=True)

        # Clean up excessive whitespace and blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned = "\n".join(lines)

        # Remove very long garbage strings (base64 images, encoded data)
        cleaned = re.sub(r'[A-Za-z0-9+/=]{200,}', '[ENCODED_DATA_REMOVED]', cleaned)

        # Limit content length to avoid overwhelming the AI model
        max_chars = 15000
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars] + "\n\n[CONTENT TRUNCATED - Page too large]"

        logger.info(f"✅ Cleaned content: {len(cleaned)} characters")
        return cleaned

    def _scrape_fast(self, url: str) -> Optional[str]:
        """
        Fast HTTP-based scraper agent using requests.
        Bypasses browser rendering for instantly scraping raw HTML when possible.
        """
        logger.info("⚡ Attempting fast HTTP scraping (Agent 1)...")
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.warning(f"⚠️ Fast scraper returned status code {response.status_code}")
                return None

            raw_html = response.text

            # Check for bot detection pages (CAPTCHA, Cloudflare, etc.)
            bot_indicators = [
                "captcha",
                "robot check",
                "challenge-platform",
                "bot protection",
                "security check",
                "automated access",
            ]
            if any(indicator in raw_html.lower() for indicator in bot_indicators):
                logger.warning("⚠️ Bot detection detected in fast scraping response")
                return None

            return raw_html
        except Exception as e:
            logger.warning(f"⚠️ Fast scraper failed with error: {e}")
            return None

    def scrape(self, url: str) -> str:
        """
        Main scraping method. Takes a URL and returns clean text content.
        First attempts fast HTTP scraping. If it fails or returns insufficient content,
        falls back to dynamic Selenium browser scraping.

        Args:
            url: The ecommerce page URL to scrape

        Returns:
            Clean text content extracted from the page, including product links

        Raises:
            RuntimeError: If scraping fails at any stage
        """
        # Step 1: Attempt Fast HTTP Scraping (Agent 1)
        try:
            raw_html = self._scrape_fast(url)
            if raw_html:
                cleaned_text = self._clean_html(raw_html)
                # Check for sufficient product/pricing signals
                price_matches = re.findall(r'₹[\d,]+|Rs\.?\s*[\d,]+|\$[\d,.]+', cleaned_text)
                if len(price_matches) >= 3:
                    logger.info(f"✨ Ultrafast scrape succeeded in <1s ({len(price_matches)} price matches)")
                    # ── ADDED: append product links to content ──
                    product_links = self._extract_product_links(raw_html, url)
                    return cleaned_text + product_links
                    # ────────────────────────────────────────────
                else:
                    logger.info("⚠️ Fast scrape lacked product signals, falling back to dynamic scraping...")
            else:
                logger.info("⚠️ Fast scrape yielded no content, falling back to dynamic scraping...")
        except Exception as e:
            logger.warning(f"⚠️ Fast scrape failed: {e}. Falling back to dynamic scraping...")

        # Step 2: Dynamic Selenium Scraping (Agent 2)
        logger.info("🌐 Launching Dynamic Selenium Scraper (Agent 2)...")
        driver = None
        try:
            # Step 2.1: Launch browser
            driver = self._launch_browser()

            # Step 2.2: Navigate to URL
            logger.info(f"🌐 Navigating to: {url}")
            driver.get(url)

            # Step 2.3: Wait for content
            self._wait_for_content(driver)

            # Step 2.4: Scroll for lazy-loaded content
            self._scroll_page(driver)

            # Step 2.5: Extract HTML
            raw_html = self._extract_html(driver)
            logger.info(f"📄 Extracted {len(raw_html)} characters of HTML")

            # Step 2.6: Clean content
            cleaned_text = self._clean_html(raw_html)

            if not cleaned_text or len(cleaned_text) < 50:
                raise RuntimeError("Page content too short — site may have blocked scraping")

            # ── ADDED: append product links to content ──
            product_links = self._extract_product_links(raw_html, url)
            return cleaned_text + product_links
            # ────────────────────────────────────────────

        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            raise RuntimeError(f"Scraping failed for {url}: {e}")

        finally:
            # Always close browser to prevent resource leaks
            if driver:
                try:
                    driver.quit()
                    logger.info("🔒 Browser closed successfully")
                except Exception:
                    pass


# -------------------------------------------------------------------
# Quick test
# -------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # In case stdout doesn't support reconfigure in some environments
    logging.basicConfig(level=logging.INFO)
    scraper = EcommerceScraper()
    test_url = "https://www.amazon.in/s?k=laptops"
    content = scraper.scrape(test_url)
    print(content[:2000])