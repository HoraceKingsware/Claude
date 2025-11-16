"""
美团自动登录模块
实现美团网站的自动登录流程
"""
import asyncio
from pathlib import Path
from typing import Optional, Dict
from loguru import logger
from .config import Config
from .browser_automation import BrowserAutomation
from .captcha_solver import CaptchaSolver
from .anti_crawler import AntiCrawlerBypass


class MeituanAutoLogin:
    """美团自动登录类"""

    # 美团登录页面的选择器
    SELECTORS = {
        # 账号密码登录标签
        'password_tab': 'text=密码登录',
        'account_tab': 'text=账号密码登录',

        # 输入框
        'username_input': 'input[placeholder*="手机号"], input[name="username"], input[type="tel"]',
        'password_input': 'input[type="password"], input[placeholder*="密码"]',

        # 登录按钮
        'login_button': 'button:has-text("登录"), button[type="submit"]',

        # 验证码
        'captcha_image': 'img[alt*="验证码"], img.captcha, .captcha-img img',
        'captcha_input': 'input[placeholder*="验证码"], input[name="captcha"]',
        'refresh_captcha': '.captcha-refresh, .refresh-captcha',

        # 滑块验证码
        'slider_container': '.geetest_slider, .slide-verify, .slider-verify',
        'slider_button': '.geetest_slider_button, .slide-btn, .slider-btn',

        # 登录成功标识
        'user_info': '.user-name, .username, [class*="user"]',
        'avatar': '.avatar, .user-avatar',

        # 错误提示
        'error_message': '.error-msg, .error-tip, [class*="error"]',
    }

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化美团自动登录

        Args:
            config_path: 配置文件路径
        """
        self.config = Config(config_path)
        self.browser = BrowserAutomation(self.config)
        self.captcha_solver = CaptchaSolver(self.config)
        self.anti_crawler = AntiCrawlerBypass(self.config)

    async def login(self, username: str = None, password: str = None) -> bool:
        """
        执行自动登录

        Args:
            username: 用户名（手机号），不传则使用配置文件
            password: 密码，不传则使用配置文件

        Returns:
            是否登录成功
        """
        # 使用传入的账号或配置文件中的账号
        username = username or self.config.username
        password = password or self.config.password

        if not username or not password:
            logger.error("未配置用户名或密码")
            return False

        try:
            # 启动浏览器
            await self.browser.start()

            # 尝试加载已保存的Cookie
            cookie_file = Path("./cookies/meituan_cookies.json")
            if cookie_file.exists():
                logger.info("发现已保存的Cookie，尝试使用Cookie登录...")
                await self.browser.load_cookies(str(cookie_file))

                # 访问美团首页检查是否已登录
                if await self._check_login_status():
                    logger.info("Cookie有效，已自动登录")
                    return True
                else:
                    logger.info("Cookie已失效，继续账号密码登录")

            # 访问登录页面
            login_url = self.config.login_url
            if not await self.browser.goto(login_url):
                logger.error("无法访问登录页面")
                return False

            # 随机滚动，模拟人类行为
            await self.anti_crawler.scroll_randomly(self.browser.page)

            # 切换到密码登录
            await self._switch_to_password_login()

            # 输入账号密码
            await self._input_credentials(username, password)

            # 处理验证码
            if not await self._handle_captcha():
                logger.error("验证码处理失败")
                return False

            # 点击登录按钮
            await self._click_login_button()

            # 等待登录结果
            login_success = await self._wait_for_login_result()

            if login_success:
                logger.info("登录成功！")

                # 保存Cookie
                await self._save_cookies()

                return True
            else:
                logger.error("登录失败")
                return False

        except Exception as e:
            logger.exception(f"登录过程发生错误: {str(e)}")
            return False

    async def _check_login_status(self) -> bool:
        """
        检查是否已登录

        Returns:
            是否已登录
        """
        try:
            # 访问美团个人中心或首页
            await self.browser.goto("https://www.meituan.com/")
            await asyncio.sleep(2)

            # 检查是否有用户信息元素
            is_logged_in = (
                await self.browser.is_element_visible(self.SELECTORS['user_info']) or
                await self.browser.is_element_visible(self.SELECTORS['avatar'])
            )

            return is_logged_in

        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return False

    async def _switch_to_password_login(self):
        """切换到密码登录标签页"""
        try:
            # 尝试点击密码登录标签
            for selector in [self.SELECTORS['password_tab'], self.SELECTORS['account_tab']]:
                if await self.browser.wait_for_selector(selector, timeout=3000):
                    await self.browser.click(selector)
                    await self.anti_crawler.random_delay(0.5, 1.5)
                    logger.info("已切换到密码登录")
                    return
        except Exception as e:
            logger.debug(f"切换登录方式时出错（可能已在密码登录页面）: {str(e)}")

    async def _input_credentials(self, username: str, password: str):
        """
        输入账号密码

        Args:
            username: 用户名
            password: 密码
        """
        logger.info("正在输入账号密码...")

        # 等待用户名输入框出现
        if await self.browser.wait_for_selector(self.SELECTORS['username_input'], timeout=5000):
            # 输入用户名
            await self.browser.type_text(self.SELECTORS['username_input'], username, human_like=True)
            await self.anti_crawler.random_delay(0.5, 1.0)

        # 等待密码输入框出现
        if await self.browser.wait_for_selector(self.SELECTORS['password_input'], timeout=5000):
            # 输入密码
            await self.browser.type_text(self.SELECTORS['password_input'], password, human_like=True)
            await self.anti_crawler.random_delay(0.5, 1.0)

        logger.info("账号密码已输入")

    async def _handle_captcha(self) -> bool:
        """
        处理验证码

        Returns:
            是否成功处理验证码
        """
        # 等待一下，看是否出现验证码
        await asyncio.sleep(1)

        # 检查是否有图片验证码
        if await self.browser.is_element_visible(self.SELECTORS['captcha_image']):
            logger.info("检测到图片验证码")
            return await self._handle_image_captcha()

        # 检查是否有滑块验证码
        if await self.browser.is_element_visible(self.SELECTORS['slider_container']):
            logger.info("检测到滑块验证码")
            return await self._handle_slider_captcha()

        # 没有验证码或验证码类型未识别
        logger.info("未检测到验证码或验证码已自动通过")
        return True

    async def _handle_image_captcha(self) -> bool:
        """
        处理图片验证码

        Returns:
            是否成功
        """
        max_retries = 3

        for attempt in range(max_retries):
            try:
                logger.info(f"尝试识别图片验证码 ({attempt + 1}/{max_retries})...")

                # 截取验证码图片
                captcha_image = await self.browser.screenshot_element(self.SELECTORS['captcha_image'])

                if not captcha_image:
                    logger.error("无法截取验证码图片")
                    return False

                # 使用AI识别验证码
                captcha_text = await self.captcha_solver.solve_captcha(captcha_image, captcha_type="text")

                if not captcha_text:
                    logger.warning("验证码识别失败")
                    # 刷新验证码
                    if await self.browser.is_element_visible(self.SELECTORS['refresh_captcha']):
                        await self.browser.click(self.SELECTORS['refresh_captcha'])
                        await asyncio.sleep(1)
                    continue

                # 输入验证码
                if await self.browser.wait_for_selector(self.SELECTORS['captcha_input'], timeout=3000):
                    await self.browser.type_text(self.SELECTORS['captcha_input'], captcha_text, human_like=False)
                    logger.info(f"已输入验证码: {captcha_text}")
                    await asyncio.sleep(1)
                    return True

            except Exception as e:
                logger.error(f"处理图片验证码时出错: {str(e)}")

        return False

    async def _handle_slider_captcha(self) -> bool:
        """
        处理滑块验证码

        Returns:
            是否成功
        """
        try:
            logger.info("正在处理滑块验证码...")

            # 等待滑块按钮出现
            if not await self.browser.wait_for_selector(self.SELECTORS['slider_button'], timeout=5000):
                logger.error("找不到滑块按钮")
                return False

            # 获取滑块按钮
            slider_button = await self.browser.page.query_selector(self.SELECTORS['slider_button'])
            if not slider_button:
                return False

            # 获取滑块的位置和大小
            box = await slider_button.bounding_box()
            if not box:
                return False

            # 这里实现简单的滑块拖动
            # 实际应用中，可能需要更复杂的算法来模拟人类滑动轨迹
            start_x = box['x'] + box['width'] / 2
            start_y = box['y'] + box['height'] / 2

            # 滑动距离（这里使用简单的固定值，实际应该通过图像识别获取缺口位置）
            # 可以使用captcha_solver的solve_slide_captcha方法
            slide_distance = 260  # 示例值

            # 模拟人类滑动轨迹
            await self._simulate_slide(start_x, start_y, slide_distance)

            # 等待验证结果
            await asyncio.sleep(2)

            # 检查是否验证成功（滑块消失或出现成功提示）
            slider_visible = await self.browser.is_element_visible(self.SELECTORS['slider_container'])

            if not slider_visible:
                logger.info("滑块验证成功")
                return True
            else:
                logger.warning("滑块验证可能失败")
                return False

        except Exception as e:
            logger.error(f"处理滑块验证码时出错: {str(e)}")
            return False

    async def _simulate_slide(self, start_x: float, start_y: float, distance: float):
        """
        模拟人类滑动轨迹

        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            distance: 滑动距离
        """
        page = self.browser.page

        # 移动到起始位置
        await page.mouse.move(start_x, start_y)
        await asyncio.sleep(0.1)

        # 按下鼠标
        await page.mouse.down()
        await asyncio.sleep(0.1)

        # 分段滑动，模拟人类行为
        steps = 20
        for i in range(steps):
            # 计算当前步骤的位置（使用缓动函数）
            progress = (i + 1) / steps
            # 使用ease-out缓动
            eased_progress = 1 - (1 - progress) ** 2
            current_x = start_x + distance * eased_progress

            # 添加随机抖动
            jitter_y = start_y + ((-1) ** i) * (i % 3)

            await page.mouse.move(current_x, jitter_y)
            await asyncio.sleep(0.01 + 0.01 * (i % 3))

        # 释放鼠标
        await asyncio.sleep(0.2)
        await page.mouse.up()

    async def _click_login_button(self):
        """点击登录按钮"""
        logger.info("正在点击登录按钮...")

        if await self.browser.wait_for_selector(self.SELECTORS['login_button'], timeout=5000):
            await self.browser.click(self.SELECTORS['login_button'], human_like=True)
            logger.info("已点击登录按钮")

    async def _wait_for_login_result(self, timeout: int = 10) -> bool:
        """
        等待登录结果

        Args:
            timeout: 超时时间（秒）

        Returns:
            是否登录成功
        """
        logger.info("等待登录结果...")

        # 等待页面跳转或出现用户信息
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            # 检查是否登录成功（URL变化或出现用户信息）
            current_url = self.browser.page.url
            if 'passport' not in current_url or await self.browser.is_element_visible(self.SELECTORS['user_info']):
                # 可能登录成功
                await asyncio.sleep(1)
                return await self._check_login_status()

            # 检查是否有错误提示
            if await self.browser.is_element_visible(self.SELECTORS['error_message']):
                error_text = await self.browser.get_text(self.SELECTORS['error_message'])
                logger.error(f"登录失败: {error_text}")
                return False

            await asyncio.sleep(0.5)

        # 超时，最后检查一次登录状态
        return await self._check_login_status()

    async def _save_cookies(self):
        """保存Cookie"""
        try:
            cookie_dir = Path("./cookies")
            cookie_dir.mkdir(parents=True, exist_ok=True)
            cookie_file = cookie_dir / "meituan_cookies.json"
            await self.browser.save_cookies(str(cookie_file))
        except Exception as e:
            logger.error(f"保存Cookie失败: {str(e)}")

    async def close(self):
        """关闭浏览器"""
        await self.browser.close()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
