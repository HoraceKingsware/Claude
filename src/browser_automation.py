"""
浏览器自动化模块
使用Playwright实现浏览器自动化，支持反爬虫检测绕过
"""
import asyncio
import logging
import random
from typing import Optional
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from .config import Config

logger = logging.getLogger(__name__)


class BrowserAutomation:
    """浏览器自动化控制类"""

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def initialize(self) -> None:
        """初始化浏览器"""
        logger.info("Initializing browser automation...")

        self.playwright = await async_playwright().start()

        # 根据配置选择浏览器类型
        if Config.BROWSER_TYPE == "firefox":
            browser_type = self.playwright.firefox
        elif Config.BROWSER_TYPE == "webkit":
            browser_type = self.playwright.webkit
        else:
            browser_type = self.playwright.chromium

        # 浏览器启动选项
        launch_options = {
            "headless": Config.HEADLESS,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
            ],
        }

        self.browser = await browser_type.launch(**launch_options)

        # 创建浏览器上下文，配置反爬虫参数
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": self._get_random_user_agent(),
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai",
            "permissions": ["geolocation"],
            "geolocation": {"latitude": 39.9042, "longitude": 116.4074},  # 北京
        }

        if Config.USER_DATA_DIR:
            context_options["storage_state"] = Config.USER_DATA_DIR

        self.context = await self.browser.new_context(**context_options)

        # 注入反检测脚本
        if Config.ENABLE_STEALTH:
            await self._inject_stealth_scripts()

        # 创建页面
        self.page = await self.context.new_page()
        self.page.set_default_timeout(Config.PAGE_LOAD_TIMEOUT * 1000)

        logger.info("Browser initialized successfully")

    async def _inject_stealth_scripts(self) -> None:
        """注入反检测脚本"""
        stealth_js = """
        // 覆盖 navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // 覆盖 chrome 对象
        window.chrome = {
            runtime: {},
        };

        // 覆盖 permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // 覆盖 plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // 覆盖 languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en'],
        });
        """

        await self.context.add_init_script(stealth_js)

    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]
        return random.choice(user_agents)

    async def random_delay(self, min_delay: Optional[float] = None, max_delay: Optional[float] = None) -> None:
        """随机延迟，模拟人类操作"""
        min_delay = min_delay or Config.RANDOM_DELAY_MIN
        max_delay = max_delay or Config.RANDOM_DELAY_MAX
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Random delay: {delay:.2f}s")
        await asyncio.sleep(delay)

    async def human_like_mouse_move(self, x: int, y: int) -> None:
        """人类化的鼠标移动"""
        if not self.page:
            return

        # 获取当前鼠标位置（模拟从随机位置开始）
        start_x = random.randint(0, 500)
        start_y = random.randint(0, 500)

        # 分段移动，模拟人类轨迹
        steps = random.randint(10, 20)
        for i in range(steps):
            intermediate_x = start_x + (x - start_x) * (i / steps)
            intermediate_y = start_y + (y - start_y) * (i / steps)

            # 添加随机抖动
            jitter_x = random.randint(-2, 2)
            jitter_y = random.randint(-2, 2)

            await self.page.mouse.move(
                intermediate_x + jitter_x,
                intermediate_y + jitter_y
            )
            await asyncio.sleep(random.uniform(0.001, 0.005))

    async def human_like_type(self, selector: str, text: str) -> None:
        """人类化的文字输入"""
        if not self.page:
            return

        element = await self.page.wait_for_selector(selector, timeout=Config.ELEMENT_WAIT_TIMEOUT * 1000)

        # 点击输入框
        await element.click()
        await self.random_delay(0.3, 0.8)

        # 逐字输入
        for char in text:
            await element.type(char, delay=random.randint(50, 200))

        await self.random_delay(0.2, 0.5)

    async def navigate(self, url: str, wait_until: str = "domcontentloaded", timeout: Optional[int] = None) -> None:
        """
        导航到指定URL

        Args:
            url: 目标URL
            wait_until: 等待策略 (load, domcontentloaded, networkidle, commit)
            timeout: 超时时间（毫秒），None使用默认值
        """
        if not self.page:
            raise RuntimeError("Browser not initialized")

        logger.info(f"Navigating to: {url}")

        try:
            # 使用domcontentloaded代替networkidle，更快更稳定
            timeout_ms = timeout or (Config.PAGE_LOAD_TIMEOUT * 1000)
            await self.page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            logger.info(f"Page loaded with {wait_until} strategy")
        except Exception as e:
            logger.warning(f"Navigation with {wait_until} failed: {e}, trying with load strategy")
            # 如果失败，尝试更宽松的策略
            try:
                await self.page.goto(url, wait_until="commit", timeout=timeout_ms)
                logger.info("Page loaded with commit strategy")
            except Exception as e2:
                logger.error(f"Navigation failed completely: {e2}")
                raise

        await self.random_delay()

    async def screenshot(self, path: str) -> None:
        """截图"""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        await self.page.screenshot(path=path, full_page=True)
        logger.info(f"Screenshot saved to: {path}")

    async def get_cookies(self) -> list:
        """获取cookies"""
        if not self.context:
            raise RuntimeError("Browser not initialized")

        return await self.context.cookies()

    async def set_cookies(self, cookies: list) -> None:
        """设置cookies"""
        if not self.context:
            raise RuntimeError("Browser not initialized")

        await self.context.add_cookies(cookies)

    async def close(self) -> None:
        """关闭浏览器"""
        logger.info("Closing browser...")

        if self.page:
            await self.page.close()

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

        logger.info("Browser closed")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()
