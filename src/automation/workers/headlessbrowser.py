import platform

import asyncio
import json
from PySide6.QtCore import QObject, Signal

from playwright.async_api import BrowserContext, async_playwright

from qasync import asyncSlot

from utils import LOGIN_METADATA
from utils.constant import Platform

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if platform.system() == "Darwin":
    EDGE_PATH = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class TestAccountWorker(QObject):
    result = Signal(int, int)
    test_result = Signal(int, int)
    test_results = Signal(list)

    def __init__(self, max_concurrent: int = 3, parent=None):
        super(TestAccountWorker, self).__init__(parent)
        self.max_concurrent = max_concurrent

    async def test_single_page(
        self,
        context: BrowserContext,
        user: dict,
    ):
        user_id = user["user_id"]
        result = -1
        try:
            page = await context.new_page()
            platform, _ = Platform.from_value(user["platform"])
            metadata = LOGIN_METADATA[platform]
            await page.context.add_cookies(json.loads(user["cookies"]))
            await page.goto(metadata["creator_url"])
            await page.wait_for_load_state("networkidle")
            element = await page.query_selector(metadata["selector"])
            if element:
                result = 1
                self.result.emit(user_id, 1)
            else:
                result = 0
                self.result.emit(user_id, 0)
        except Exception:
            self.result.emit(user_id, -1)

        finally:
            await page.close()

        return user_id, result

    @asyncSlot(list)
    async def test_all_accounts(self, users: list):
        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path=EDGE_PATH, headless=False)
            context = await browser.new_context()
            try:
                semaphore = asyncio.Semaphore(self.max_concurrent)

                async def process_with_semaphore(user):
                    async with semaphore:
                        return await self.test_single_page(context, user)

                tasks = [process_with_semaphore(user) for user in users]
                results = await asyncio.gather(*tasks)
                self.test_results.emit(results)

            except Exception as e:
                print("error", e)

            finally:
                await context.close()
                await browser.close()

    @asyncSlot(dict)
    async def test_account_state(self, user: dict):
        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path=EDGE_PATH)
            page = await browser.new_page()
            user_id = user["id"]
            platform, _ = Platform.from_value(user["platform"])
            metadata = LOGIN_METADATA[platform]
            await page.context.add_cookies(json.loads(user["cookies"]))
            await page.goto(metadata["creator_url"])
            await page.wait_for_load_state("networkidle")
            element = await page.query_selector(metadata["selector"])
            await browser.close()
            if element:
                self.test_result.emit(user_id, 1)
            else:
                self.test_result.emit(user_id, 0)
