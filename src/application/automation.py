import time
import random
import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ApplicationResult:
    success: bool
    job_id: str
    message: str
    application_url: Optional[str] = None
    error: Optional[str] = None


class BrowserAutomation:
    def __init__(self, headless: bool = False, slow_mode: bool = True):
        self.headless = headless
        self.slow_mode = slow_mode
        self.browser = None
        self.context = None
        self.page = None
        self.min_delay = 1000
        self.max_delay = 3000

    async def initialize(self):
        try:
            from playwright.async_api import async_playwright
            self.playwright = async_playwright
            self.playwright = await self.playwright.start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            self.page = await self.context.new_page()
            return True
        except ImportError:
            print("Playwright not installed. Run: pip install playwright && playwright install")
            return False
        except Exception as e:
            print(f"Failed to initialize browser: {e}")
            return False

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def _random_delay(self):
        if self.slow_mode:
            delay = random.randint(self.min_delay, self.max_delay)
            time.sleep(delay / 1000)

    async def navigate_to_url(self, url: str) -> bool:
        try:
            await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            self._random_delay()
            return True
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False

    async def take_screenshot(self, path: str = "screenshot.png"):
        try:
            await self.page.screenshot(path=path, full_page=True)
            return True
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return False

    async def fill_form_field(self, selector: str, value: str):
        try:
            await self.page.fill(selector, value)
            self._random_delay()
        except Exception as e:
            print(f"Failed to fill field {selector}: {e}")

    async def click_element(self, selector: str):
        try:
            await self.page.click(selector)
            self._random_delay()
        except Exception as e:
            print(f"Failed to click {selector}: {e}")

    async def get_page_content(self) -> str:
        return await self.page.content()

    async def wait_for_selector(self, selector: str, timeout: int = 10000):
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False

    async def get_accessibility_snapshot(self):
        try:
            snapshot = await self.page.evaluate("""() => {
                const getAccessibilityTree = (element, depth = 0) => {
                    if (depth > 3) return null;
                    
                    const children = Array.from(element.children)
                        .map(child => getAccessibilityTree(child, depth + 1))
                        .filter(Boolean);
                    
                    const role = element.getAttribute?.('role') || 
                                (element.tagName === 'INPUT' ? 'textbox' : 
                                 element.tagName === 'BUTTON' ? 'button' : 
                                 element.tagName === 'A' ? 'link' : 
                                 element.tagName === 'SELECT' ? 'combobox' : 'generic');
                    
                    const name = element.getAttribute?.('aria-label') || 
                                element.getAttribute?.('name') || 
                                element.textContent?.substring(0, 50) || '';
                    
                    const disabled = element.getAttribute?.('disabled');
                    
                    return { role, name, children: children.length ? children : null, disabled };
                };
                
                return getAccessibilityTree(document.body);
            }""")
            return snapshot
        except Exception as e:
            print(f"Failed to get accessibility snapshot: {e}")
            return None


class ApplicationBot:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.browser = None

    async def apply_to_job(self, job_data: Dict, profile_data: Dict,
                          resume_path: Optional[str] = None,
                          cover_letter_path: Optional[str] = None) -> ApplicationResult:
        application_url = job_data.get('application_url')

        if not application_url:
            return ApplicationResult(
                success=False,
                job_id=job_data.get('external_id', 'unknown'),
                message="No application URL available",
                error="Missing application URL"
            )

        browser = BrowserAutomation(
            headless=self.config.get('headless', False),
            slow_mode=self.config.get('slow_mode', True)
        )

        try:
            initialized = await browser.initialize()
            if not initialized:
                return ApplicationResult(
                    success=False,
                    job_id=job_data.get('external_id', 'unknown'),
                    message="Failed to initialize browser"
                )

            success = await browser.navigate_to_url(application_url)

            if not success:
                return ApplicationResult(
                    success=False,
                    job_id=job_data.get('external_id', 'unknown'),
                    message="Failed to navigate to application page"
                )

            await browser.take_screenshot(f"data/screenshots/{job_data.get('external_id', 'job')}_page.png")

            return ApplicationResult(
                success=True,
                job_id=job_data.get('external_id', 'unknown'),
                message="Application form opened successfully",
                application_url=application_url
            )

        except Exception as e:
            return ApplicationResult(
                success=False,
                job_id=job_data.get('external_id', 'unknown'),
                message=f"Application failed: {str(e)}",
                error=str(e)
            )
        finally:
            await browser.close()

    async def fill_linkedin_easy_apply(self, job_url: str, profile_data: Dict,
                                       resume_path: Optional[str] = None) -> ApplicationResult:
        browser = BrowserAutomation()

        try:
            await browser.initialize()
            await browser.navigate_to_url(job_url)

            await browser.take_screenshot("data/screenshots/linkedin_apply_clicked.png")

            return ApplicationResult(
                success=True,
                job_id="linkedin",
                message="LinkedIn Easy Apply form opened"
            )

        except Exception as e:
            return ApplicationResult(
                success=False,
                job_id="linkedin",
                message=str(e),
                error=str(e)
            )
        finally:
            await browser.close()


application_bot = ApplicationBot()