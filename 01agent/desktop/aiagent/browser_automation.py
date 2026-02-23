import asyncio
import logging
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright, Page, Browser
from playwright_stealth import Stealth
from config_manager import config_manager
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
        self._browser_config = config_manager.get_config().browser

    async def launch_browser(self) -> Optional[Page]:
        """Launches a stealth browser instance."""
        try:
            if self._page and not self._page.is_closed():
                logger.info("Browser already launched and active.")
                return self._page

            # Use sync_playwright in a separate thread to avoid blocking asyncio loop
            loop = asyncio.get_event_loop()
            self._playwright_instance = await loop.run_in_executor(
                None, sync_playwright().__enter__
            )
            
            browser_type_instance = getattr(self._playwright_instance, self._browser_config.browser_type)
            self._browser = await loop.run_in_executor(
                None, lambda: browser_type_instance.launch(headless=self._browser_config.headless)
            )
            self._page = await loop.run_in_executor(
                None, self._browser.new_page
            )
            
            # Apply stealth to the page
            await loop.run_in_executor(None, lambda: Stealth(self._page).apply())
            
            logger.info(f"Stealth browser launched successfully (headless={self._browser_config.headless}, type={self._browser_config.browser_type}).")
            return self._page
        except Exception as e:
            logger.error(f"Failed to launch stealth browser: {e}")
            return None

    async def close_browser(self):
        """Closes the browser instance."""
        try:
            if self._browser:
                await asyncio.get_event_loop().run_in_executor(None, self._browser.close)
                self._browser = None
                self._page = None
                logger.info("Stealth browser closed.")
            if self._playwright_instance:
                await asyncio.get_event_loop().run_in_executor(None, self._playwright_instance.__exit__)
                self._playwright_instance = None
        except Exception as e:
            logger.error(f"Failed to close stealth browser: {e}")

    async def goto(self, url: str, timeout: int = 60000) -> bool:
        """Navigates to a given URL."""
        if not self._page:
            logger.warning("Browser page not available. Cannot navigate.")
            return False
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._page.goto(url, timeout=timeout)
            )
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
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._page.click(selector, timeout=timeout)
            )
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
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._page.type(selector, text, delay=delay)
            )
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
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._page.screenshot(path=path)
            )
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
            content = await asyncio.get_event_loop().run_in_executor(
                None, self._page.content
            )
            logger.info("Page content retrieved.")
            return content
        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            return None

# Global instance for easy access
browser_automation = BrowserAutomation()
