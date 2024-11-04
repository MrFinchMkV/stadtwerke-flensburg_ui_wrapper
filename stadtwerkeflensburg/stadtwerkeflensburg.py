import logging
from urllib.parse import urljoin
from .models.reading import Reading
from playwright.async_api import Browser, Page, Playwright, async_playwright

_LOGGER = logging.getLogger(__name__)


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
        _LOGGER.debug(f"E-Mail: {self.email}")
        _LOGGER.debug("Password: ***")
        _LOGGER.debug(f"Headless: {self.headless}")
        _LOGGER.debug(f"Base_URL: {self.base_url}")

    def __await__(self):
        async def closure():
            _LOGGER.debug("await")
            return self
        return closure().__await__()

    async def _async_start(self):
        _LOGGER.debug("start")
        playwright: Playwright = await async_playwright().start()
        self.browser: Browser = await playwright.chromium.launch(headless=self.headless)
        context = await self.browser.new_context()
        self.page: Page = await context.new_page()

    async def async_login(self):
        await self._async_start()
        _LOGGER.debug("login")
        path = "kundenkonto/#/loginRegistration/"
        url = urljoin(self.base_url, path)
        _LOGGER.debug(f"Goto URL: {url}")
        await self.page.goto(url)
        await self.page.get_by_text("Reject all").click()
        await self.page.get_by_text("E-Mail-Adresse", exact=True).fill(self.email)
        await self.page.get_by_text("Passwort", exact=True).fill(self.password)
        await self.page.get_by_label("loginButton").click()

    async def async_logout(self):
        _LOGGER.debug("logout")
        path = "/kundenkonto/#/loginRegistration/logout"
        url = urljoin(self.base_url, path)
        _LOGGER.debug(f"URL: {url}")
        await self.page.goto(url)

    async def async_close_browser(self):
        _LOGGER.debug("close")
        await self.browser.close()

    async def async_get_readings(self) -> list[Reading]:
        await self.page.get_by_text("Zählerstand erfassen").click()
        await self.page.wait_for_load_state("networkidle")
        table_locator = self.page.locator('table')
        row_locator = table_locator.locator('tr')
        colum_locator = row_locator.locator('td')
        colum_texts = list(dict.fromkeys(await colum_locator.all_inner_texts()))
        readings: list[Reading] = []
        for x in range(0, len(colum_texts), 2):
            reading_date = colum_texts[x]
            meter_reading = float(colum_texts[x + 1].replace(',', '.'))
            reading = Reading(reading_date, meter_reading)
            readings.append(reading)
        return readings

    async def async_get_last_reading(self) -> Reading:
        readings = await self.async_get_readings()
        return readings[0]
