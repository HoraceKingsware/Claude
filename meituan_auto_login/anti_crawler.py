"""
反爬虫突破模块
实现各种反爬虫检测绕过技术
"""
import random
import time
from typing import Dict, Any
from playwright.async_api import Page, BrowserContext
from fake_useragent import UserAgent


class AntiCrawlerBypass:
    """反爬虫突破类"""

    # 常用User-Agent列表
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]

    def __init__(self, config):
        """
        初始化反爬虫突破

        Args:
            config: 配置对象
        """
        self.config = config
        self.ua = UserAgent()

    def get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        if self.config.random_user_agent:
            try:
                return self.ua.random
            except:
                return random.choice(self.USER_AGENTS)
        return self.USER_AGENTS[0]

    def get_stealth_js(self) -> str:
        """
        获取隐身JS脚本，用于隐藏自动化特征

        Returns:
            JavaScript代码
        """
        return """
        // 隐藏webdriver特征
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // 覆盖plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });

        // 覆盖languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });

        // 覆盖chrome对象
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };

        // 覆盖permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
        );

        // 添加真实的浏览器特征
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });

        // 覆盖自动化检测
        const originalFunction = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === window.navigator.permissions.query) {
                return 'function query() { [native code] }';
            }
            return originalFunction.call(this);
        };
        """

    async def apply_stealth(self, context: BrowserContext, page: Page):
        """
        应用隐身设置到浏览器上下文和页面

        Args:
            context: 浏览器上下文
            page: 页面对象
        """
        if not self.config.stealth_mode:
            return

        # 注入隐身脚本
        await context.add_init_script(self.get_stealth_js())

        # 设置额外的HTTP头
        await page.set_extra_http_headers({
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    async def random_delay(self, min_delay: float = None, max_delay: float = None):
        """
        随机延迟，模拟人类操作

        Args:
            min_delay: 最小延迟（秒）
            max_delay: 最大延迟（秒）
        """
        if min_delay is None or max_delay is None:
            delay_range = self.config.delay_range
            min_delay = delay_range.get('min', 1.0)
            max_delay = delay_range.get('max', 3.0)

        delay = random.uniform(min_delay, max_delay)
        await self._sleep(delay)

    async def _sleep(self, seconds: float):
        """异步睡眠"""
        time.sleep(seconds)

    async def human_like_typing(self, page: Page, selector: str, text: str):
        """
        模拟人类打字行为

        Args:
            page: 页面对象
            selector: 输入框选择器
            text: 要输入的文本
        """
        if not self.config.human_behavior:
            # 如果不需要模拟人类行为，直接填充
            await page.fill(selector, text)
            return

        # 先点击输入框
        await page.click(selector)
        await self.random_delay(0.1, 0.3)

        # 逐字符输入
        for char in text:
            await page.type(selector, char, delay=random.randint(50, 150))
            # 偶尔停顿
            if random.random() < 0.1:
                await self.random_delay(0.1, 0.5)

    async def human_like_click(self, page: Page, selector: str):
        """
        模拟人类点击行为

        Args:
            page: 页面对象
            selector: 点击目标选择器
        """
        if self.config.human_behavior:
            # 先移动鼠标到元素上
            element = await page.query_selector(selector)
            if element:
                box = await element.bounding_box()
                if box:
                    # 在元素范围内随机选择点击位置
                    x = box['x'] + random.uniform(5, box['width'] - 5)
                    y = box['y'] + random.uniform(5, box['height'] - 5)
                    await page.mouse.move(x, y)
                    await self.random_delay(0.1, 0.3)

        # 执行点击
        await page.click(selector)

    async def scroll_randomly(self, page: Page):
        """
        随机滚动页面，模拟人类浏览行为

        Args:
            page: 页面对象
        """
        if not self.config.human_behavior:
            return

        # 随机滚动几次
        scroll_times = random.randint(1, 3)
        for _ in range(scroll_times):
            scroll_y = random.randint(100, 500)
            await page.evaluate(f"window.scrollBy(0, {scroll_y})")
            await self.random_delay(0.3, 0.8)

    def get_browser_args(self) -> list:
        """
        获取浏览器启动参数，用于规避检测

        Returns:
            浏览器参数列表
        """
        args = [
            '--disable-blink-features=AutomationControlled',  # 禁用自动化控制特征
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-blink-features=AutomationControlled',
        ]

        return args
