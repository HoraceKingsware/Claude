"""
浏览器自动化模块
"""
import asyncio
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger
from .anti_crawler import AntiCrawlerBypass


class BrowserAutomation:
    """浏览器自动化类"""

    def __init__(self, config):
        """
        初始化浏览器自动化

        Args:
            config: 配置对象
        """
        self.config = config
        self.anti_crawler = AntiCrawlerBypass(config)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self):
        """启动浏览器"""
        logger.info("正在启动浏览器...")

        # 启动Playwright
        self.playwright = await async_playwright().start()

        # 选择浏览器类型
        browser_type = self.config.browser_type
        if browser_type == 'chromium':
            browser_launcher = self.playwright.chromium
        elif browser_type == 'firefox':
            browser_launcher = self.playwright.firefox
        elif browser_type == 'webkit':
            browser_launcher = self.playwright.webkit
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")

        # 准备启动参数
        launch_options = {
            'headless': self.config.headless,
            'args': self.anti_crawler.get_browser_args()
        }

        # 启动浏览器
        self.browser = await browser_launcher.launch(**launch_options)
        logger.info(f"浏览器已启动: {browser_type}")

        # 创建浏览器上下文
        await self._create_context()

    async def _create_context(self):
        """创建浏览器上下文"""
        # 准备上下文选项
        context_options = {
            'viewport': self.config.viewport,
            'user_agent': self.anti_crawler.get_random_user_agent(),
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai',
        }

        # 如果配置了用户数据目录，使用持久化上下文
        user_data_dir = self.config.user_data_dir
        if user_data_dir:
            Path(user_data_dir).mkdir(parents=True, exist_ok=True)
            # 注意：持久化上下文需要使用launch_persistent_context
            # 这里先使用普通上下文，后续可以改进
            self.context = await self.browser.new_context(**context_options)
        else:
            self.context = await self.browser.new_context(**context_options)

        # 创建新页面
        self.page = await self.context.new_page()

        # 应用反爬虫设置
        await self.anti_crawler.apply_stealth(self.context, self.page)

        logger.info("浏览器上下文已创建")

    async def goto(self, url: str, wait_until: str = "networkidle") -> bool:
        """
        导航到指定URL

        Args:
            url: 目标URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle)

        Returns:
            是否成功
        """
        try:
            logger.info(f"正在访问: {url}")
            await self.page.goto(url, wait_until=wait_until, timeout=30000)
            await self.anti_crawler.random_delay()
            return True
        except Exception as e:
            logger.error(f"访问页面失败: {str(e)}")
            return False

    async def wait_for_selector(
        self,
        selector: str,
        timeout: int = 10000,
        state: str = "visible"
    ) -> bool:
        """
        等待元素出现

        Args:
            selector: CSS选择器
            timeout: 超时时间（毫秒）
            state: 元素状态 (attached, detached, visible, hidden)

        Returns:
            是否找到元素
        """
        try:
            await self.page.wait_for_selector(selector, timeout=timeout, state=state)
            return True
        except Exception as e:
            logger.warning(f"等待元素超时: {selector}, 错误: {str(e)}")
            return False

    async def type_text(self, selector: str, text: str, human_like: bool = True):
        """
        输入文本

        Args:
            selector: 输入框选择器
            text: 要输入的文本
            human_like: 是否模拟人类输入
        """
        if human_like and self.config.human_behavior:
            await self.anti_crawler.human_like_typing(self.page, selector, text)
        else:
            await self.page.fill(selector, text)

    async def click(self, selector: str, human_like: bool = True):
        """
        点击元素

        Args:
            selector: 元素选择器
            human_like: 是否模拟人类点击
        """
        if human_like and self.config.human_behavior:
            await self.anti_crawler.human_like_click(self.page, selector)
        else:
            await self.page.click(selector)

    async def screenshot(self, path: str = None) -> bytes:
        """
        截图

        Args:
            path: 保存路径（可选）

        Returns:
            截图数据
        """
        screenshot_options = {}
        if path:
            screenshot_options['path'] = path

        return await self.page.screenshot(**screenshot_options)

    async def screenshot_element(self, selector: str, path: str = None) -> Optional[bytes]:
        """
        截取元素

        Args:
            selector: 元素选择器
            path: 保存路径（可选）

        Returns:
            截图数据
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                screenshot_options = {}
                if path:
                    screenshot_options['path'] = path
                return await element.screenshot(**screenshot_options)
        except Exception as e:
            logger.error(f"元素截图失败: {str(e)}")

        return None

    async def get_cookies(self) -> list:
        """获取所有Cookie"""
        return await self.context.cookies()

    async def save_cookies(self, path: str):
        """
        保存Cookie到文件

        Args:
            path: 保存路径
        """
        import json
        cookies = await self.get_cookies()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        logger.info(f"Cookie已保存到: {path}")

    async def load_cookies(self, path: str):
        """
        从文件加载Cookie

        Args:
            path: Cookie文件路径
        """
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            await self.context.add_cookies(cookies)
            logger.info(f"已加载Cookie: {path}")
        except Exception as e:
            logger.error(f"加载Cookie失败: {str(e)}")

    async def execute_script(self, script: str):
        """
        执行JavaScript代码

        Args:
            script: JavaScript代码

        Returns:
            执行结果
        """
        return await self.page.evaluate(script)

    async def is_element_visible(self, selector: str) -> bool:
        """
        检查元素是否可见

        Args:
            selector: 元素选择器

        Returns:
            是否可见
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.is_visible()
        except:
            pass
        return False

    async def get_text(self, selector: str) -> str:
        """
        获取元素文本

        Args:
            selector: 元素选择器

        Returns:
            文本内容
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.text_content()
        except:
            pass
        return ""

    async def close(self):
        """关闭浏览器"""
        logger.info("正在关闭浏览器...")

        if self.page:
            await self.page.close()

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

        logger.info("浏览器已关闭")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
