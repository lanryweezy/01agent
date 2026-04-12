import asyncio
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser
from enum import Enum

logger = logging.getLogger(__name__)

class BrowserCommand(Enum):
    GOTO = "goto"
    CLICK = "click"
    TYPE_TEXT = "type_text"
    SCREENSHOT = "screenshot"
    GET_PAGE_CONTENT = "get_page_content"

class BrowserAutomation:
    def __init__(self):
        self._playwright_instance = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

    async def launch_browser(self, headless: bool = False, browser_type: str = "chromium") -> Optional[Page]:
        """Launches a browser instance."""
        try:
            if self._page and not self._page.is_closed():
                logger.info("Browser already launched and active.")
                return self._page

            self._playwright_instance = await async_playwright().start()
            
            browser_launcher = getattr(self._playwright_instance, browser_type)
            self._browser = await browser_launcher.launch(headless=headless)
            self._page = await self._browser.new_page()
            
            logger.info(f"Browser launched successfully (headless={headless}, type={browser_type}).")
            return self._page
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")
            return None

    async def close_browser(self):
        """Closes the browser instance."""
        try:
            if self._browser:
                await self._browser.close()
                self._browser = None
                self._page = None
                logger.info("Browser closed.")
            if self._playwright_instance:
                await self._playwright_instance.stop()
                self._playwright_instance = None
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")

    async def goto(self, url: str, timeout: int = 60000) -> bool:
        """Navigates to a given URL."""
        if not self._page:
            logger.warning("Browser page not available. Cannot navigate.")
            return False
        try:
            await self._page.goto(url, timeout=timeout)
            logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False

    async def click(self, selector: str, timeout: int = 30000) -> bool:
        """Clicks on an element identified by a CSS selector."""
        if not self._page:
            logger.warning("Browser page not available. Cannot click.")
            return False
        try:
            await self._page.click(selector, timeout=timeout)
            logger.info(f"Clicked on {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to click on {selector}: {e}")
            return False

    async def type_text(self, selector: str, text: str, delay: int = 50) -> bool:
        """Types text into an element identified by a CSS selector."""
        if not self._page:
            logger.warning("Browser page not available. Cannot type text.")
            return False
        try:
            await self._page.type(selector, text, delay=delay)
            logger.info(f"Typed '{text[:20]}...' into {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to type text into {selector}: {e}")
            return False

    async def screenshot(self, path: str = "screenshot.png") -> bool:
        """Takes a screenshot of the current page."""
        if not self._page:
            logger.warning("Browser page not available. Cannot take screenshot.")
            return False
        try:
            await self._page.screenshot(path=path)
            logger.info(f"Screenshot saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False

    async def get_page_content(self) -> Optional[str]:
        """Returns the full HTML content of the current page."""
        if not self._page:
            logger.warning("Browser page not available. Cannot get content.")
            return None
        try:
            content = await self._page.content()
            logger.info("Page content retrieved.")
            return content
        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            return None

# Global instance for easy access
browser_automation = BrowserAutomation()
