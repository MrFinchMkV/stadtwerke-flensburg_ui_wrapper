# import asyncio
import logging
# from datetime import date
from urllib.parse import urljoin
from .models.reading import Reading
from playwright.async_api import Browser, Page, Playwright, async_playwright

from time import sleep

logger = logging.getLogger(__name__)


class StadtwerkeFlensburg():
    base_url: str = "https://www.stadtwerke-flensburg.de"

    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = True
    ) -> None:
        self.email = email
        self.password = password
        self.headless = headless
        logging.basicConfig(level=logging.DEBUG)
        logger.debug(f"E-Mail: {self.email}")
        logger.debug("Password: ***")
        logger.debug(f"Headless: {self.headless}")
        logger.debug(f"Base_URL: {self.base_url}")

    def __await__(self):
        async def closure():
            logger.debug("await")
            return self
        return closure().__await__()

    async def async_start(self):
        logger.debug("start")
        playwright: Playwright = await async_playwright().start()
        self.browser: Browser = await playwright.chromium.launch(headless=self.headless)
        context = await self.browser.new_context()
        self.page: Page = await context.new_page()

    async def async_login(self):
        logger.debug("login")
        path = "kundenkonto/#/loginRegistration/"
        url = urljoin(self.base_url, path)
        logger.debug(f"Goto URL: {url}")
        await self.page.goto(url)
        await self.page.get_by_text("Reject all").click()
        await self.page.get_by_text("E-Mail-Adresse", exact=True).fill(self.email)
        await self.page.get_by_text("Passwort", exact=True).fill(self.password)
        await self.page.get_by_label("loginButton").click()

    async def async_logout(self):
        logger.debug("logout")
        path = "/kundenkonto/#/loginRegistration/logout"
        url = urljoin(self.base_url, path)
        logger.debug(f"URL: {url}")
        await self.page.goto(url)

    async def async_close_browser(self):
        logger.debug("close")
        await self.browser.close()

    async def async_get_meter_readings(self) -> list[Reading]:
        await self.page.get_by_text("Zählerstand erfassen").click()
        sleep(1)
        table_locator = self.page.locator('table')
        row_locator = table_locator.locator('tr')
        colum_locator = row_locator.locator('td')
        colum_texts = list(dict.fromkeys(await colum_locator.all_inner_texts()))
        readings: list[Reading] = []
        for x in range(0, len(colum_texts), 2):
            reading_date = colum_texts[x]
            meter_reading = colum_texts[x + 1]
            reading = Reading(reading_date, meter_reading)
            readings.append(reading)
        return readings

    async def async_get_last_meter_reading(self) -> Reading:
        readings = await self.async_get_meter_readings()
        return readings[0]
