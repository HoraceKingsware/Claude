"""
京东自动登录核心模块
整合浏览器自动化、AI验证码识别、反爬虫策略，实现京东网站自动登录
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from .browser_automation import BrowserAutomation
from .captcha_solver import CaptchaSolver
from .anti_crawler import AntiCrawlerStrategy
from .config import Config

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE) if Config.LOG_FILE else logging.NullHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class JDAutoLogin:
    """京东自动登录主类"""

    def __init__(self):
        self.browser: Optional[BrowserAutomation] = None
        self.captcha_solver: Optional[CaptchaSolver] = None
        self.anti_crawler: Optional[AntiCrawlerStrategy] = None
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)

    async def login(self) -> bool:
        """
        执行自动登录

        Returns:
            bool: 登录成功返回True，失败返回False
        """
        logger.info("Starting JD auto login...")

        # 验证配置
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return False

        # 初始化组件
        self.browser = BrowserAutomation()
        self.captcha_solver = CaptchaSolver()

        try:
            # 初始化浏览器
            await self.browser.initialize()
            self.anti_crawler = AntiCrawlerStrategy(self.browser.page)

            # 执行登录流程，支持重试
            for attempt in range(Config.MAX_RETRY_TIMES):
                logger.info(f"Login attempt {attempt + 1}/{Config.MAX_RETRY_TIMES}")

                success = await self._login_attempt()

                if success:
                    logger.info("Login successful!")
                    return True

                if attempt < Config.MAX_RETRY_TIMES - 1:
                    logger.warning(f"Login failed, retrying in {Config.RETRY_DELAY}s...")
                    await asyncio.sleep(Config.RETRY_DELAY)

            logger.error("All login attempts failed")
            return False

        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return False

        finally:
            # 清理资源
            if self.browser:
                await self.browser.close()

    async def _login_attempt(self) -> bool:
        """单次登录尝试"""
        try:
            # 1. 访问登录页面
            await self._navigate_to_login_page()

            # 2. 处理可能的Cookie同意弹窗
            await self.anti_crawler.handle_cookie_consent()

            # 3. 模拟人类行为
            await self.anti_crawler.simulate_reading(2, 4)

            # 4. 选择账号密码登录方式
            await self._select_password_login()

            # 5. 输入账号密码
            await self._input_credentials()

            # 6. 处理验证码
            captcha_handled = await self._handle_captcha()
            if not captcha_handled:
                logger.warning("Failed to handle captcha")
                return False

            # 7. 点击登录按钮
            await self._click_login_button()

            # 8. 等待登录结果
            login_success = await self._wait_for_login_result()

            if login_success:
                # 保存登录状态
                await self._save_login_state()

            return login_success

        except Exception as e:
            logger.error(f"Login attempt error: {e}", exc_info=True)
            # 保存错误截图
            await self._save_error_screenshot()
            return False

    async def _navigate_to_login_page(self) -> None:
        """访问登录页面"""
        logger.info(f"Navigating to login page: {Config.JD_LOGIN_URL}")

        await self.browser.navigate(Config.JD_LOGIN_URL)

        # 绕过WebDriver检测
        await self.anti_crawler.bypass_webdriver_detection()

        # 注入指纹伪装
        await self.anti_crawler.inject_fingerprint_spoofing()

        # 等待页面加载完成
        await self.anti_crawler.wait_for_network_idle()

        logger.info("Login page loaded")

    async def _select_password_login(self) -> None:
        """选择账号密码登录方式"""
        logger.info("Selecting password login method...")

        try:
            # 可能的账号密码登录标签选择器
            selectors = [
                '.login-tab-r',
                'a:has-text("账户登录")',
                'a:has-text("账号登录")',
                '.login-tab:has-text("账户")',
            ]

            for selector in selectors:
                try:
                    element = await self.browser.page.wait_for_selector(
                        selector,
                        timeout=5000,
                        state="visible"
                    )
                    if element:
                        await element.click()
                        logger.info(f"Clicked password login tab: {selector}")
                        await self.browser.random_delay(0.5, 1.5)
                        return
                except Exception:
                    continue

            logger.warning("Could not find password login tab, assuming already selected")

        except Exception as e:
            logger.warning(f"Error selecting password login: {e}")

    async def _input_credentials(self) -> None:
        """输入账号密码"""
        logger.info("Inputting credentials...")

        # 用户名输入框选择器
        username_selectors = [
            '#loginname',
            'input[name="loginname"]',
            'input[placeholder*="邮箱"]',
            'input[placeholder*="用户名"]',
            'input[type="text"]',
        ]

        # 密码输入框选择器
        password_selectors = [
            '#nloginpwd',
            'input[name="nloginpwd"]',
            'input[type="password"]',
            'input[placeholder*="密码"]',
        ]

        # 输入用户名
        for selector in username_selectors:
            try:
                element = await self.browser.page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )
                if element:
                    await self.browser.human_like_type(selector, Config.JD_USERNAME)
                    logger.info("Username input completed")
                    break
            except Exception:
                continue

        await self.browser.random_delay(0.5, 1.0)

        # 输入密码
        for selector in password_selectors:
            try:
                element = await self.browser.page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )
                if element:
                    await self.browser.human_like_type(selector, Config.JD_PASSWORD)
                    logger.info("Password input completed")
                    break
            except Exception:
                continue

        await self.browser.random_delay(0.5, 1.5)

    async def _handle_captcha(self) -> bool:
        """处理验证码"""
        logger.info("Checking for captcha...")

        try:
            # 检查是否有验证码
            captcha_selectors = [
                '.captcha-img',
                '#JD_Verification1',
                'img[src*="captcha"]',
                'img[src*="verify"]',
                '.JDJRV-slide-bg',  # 滑块验证码背景
            ]

            captcha_found = False
            captcha_type = None

            for selector in captcha_selectors:
                try:
                    element = await self.browser.page.wait_for_selector(
                        selector,
                        timeout=3000,
                        state="visible"
                    )
                    if element:
                        captcha_found = True
                        # 判断验证码类型
                        if 'slide' in selector.lower():
                            captcha_type = 'slider'
                        else:
                            captcha_type = 'text'
                        logger.info(f"Captcha detected: {captcha_type}")
                        break
                except Exception:
                    continue

            if not captcha_found:
                logger.info("No captcha detected")
                return True

            # 根据验证码类型处理
            if captcha_type == 'text':
                return await self._solve_text_captcha()
            elif captcha_type == 'slider':
                return await self._solve_slider_captcha()

            return True

        except Exception as e:
            logger.error(f"Error handling captcha: {e}", exc_info=True)
            return False

    async def _solve_text_captcha(self) -> bool:
        """处理文字验证码"""
        logger.info("Solving text captcha...")

        try:
            # 截取验证码图片
            captcha_img_path = self.screenshot_dir / "captcha_text.png"

            # 查找验证码图片元素
            captcha_img = await self.browser.page.query_selector('.captcha-img, img[src*="captcha"]')
            if not captcha_img:
                logger.error("Captcha image not found")
                return False

            # 截图
            await captcha_img.screenshot(path=str(captcha_img_path))
            logger.info(f"Captcha screenshot saved: {captcha_img_path}")

            # 使用AI识别验证码
            captcha_text = await self.captcha_solver.solve_text_captcha(str(captcha_img_path))

            if not captcha_text:
                logger.error("Failed to solve captcha")
                return False

            logger.info(f"Captcha solved: {captcha_text}")

            # 输入验证码
            captcha_input_selectors = [
                '#authcode',
                'input[name="authcode"]',
                '.captcha-input',
            ]

            for selector in captcha_input_selectors:
                try:
                    element = await self.browser.page.wait_for_selector(
                        selector,
                        timeout=3000,
                        state="visible"
                    )
                    if element:
                        await self.browser.human_like_type(selector, captcha_text)
                        logger.info("Captcha input completed")
                        await self.browser.random_delay(0.3, 0.8)
                        return True
                except Exception:
                    continue

            logger.error("Captcha input field not found")
            return False

        except Exception as e:
            logger.error(f"Error solving text captcha: {e}", exc_info=True)
            return False

    async def _solve_slider_captcha(self) -> bool:
        """处理滑块验证码"""
        logger.info("Solving slider captcha...")

        try:
            # 截取滑块验证码图片
            bg_img_path = self.screenshot_dir / "captcha_slider_bg.png"
            slider_img_path = self.screenshot_dir / "captcha_slider.png"

            # 查找背景图和滑块图
            bg_img = await self.browser.page.query_selector('.JDJRV-slide-bg, .slide-bg')
            slider_img = await self.browser.page.query_selector('.JDJRV-slide-block, .slide-block')

            if not bg_img or not slider_img:
                logger.error("Slider captcha elements not found")
                return False

            # 截图
            await bg_img.screenshot(path=str(bg_img_path))
            await slider_img.screenshot(path=str(slider_img_path))

            logger.info(f"Slider captcha screenshots saved")

            # 使用AI识别滑块距离
            distance = await self.captcha_solver.solve_slider_captcha(
                str(bg_img_path),
                str(slider_img_path)
            )

            if not distance:
                logger.error("Failed to solve slider captcha")
                return False

            logger.info(f"Slider distance: {distance}px")

            # 执行滑块拖动
            await self._drag_slider(distance)

            return True

        except Exception as e:
            logger.error(f"Error solving slider captcha: {e}", exc_info=True)
            return False

    async def _drag_slider(self, distance: int) -> None:
        """拖动滑块"""
        logger.info(f"Dragging slider {distance}px...")

        try:
            # 查找滑块按钮
            slider_button = await self.browser.page.query_selector('.JDJRV-slide-btn, .slide-btn')
            if not slider_button:
                logger.error("Slider button not found")
                return

            # 获取滑块位置
            box = await slider_button.bounding_box()
            if not box:
                logger.error("Failed to get slider bounding box")
                return

            start_x = box['x'] + box['width'] / 2
            start_y = box['y'] + box['height'] / 2

            # 移动到滑块
            await self.browser.page.mouse.move(start_x, start_y)
            await asyncio.sleep(0.2)

            # 按下鼠标
            await self.browser.page.mouse.down()
            await asyncio.sleep(0.1)

            # 模拟人类拖动轨迹（加速->匀速->减速）
            steps = 30
            for i in range(steps):
                # 计算当前位置
                progress = (i + 1) / steps

                # 使用贝塞尔曲线模拟人类轨迹
                if progress < 0.3:  # 加速阶段
                    factor = progress / 0.3
                    current_distance = distance * 0.3 * (factor ** 2)
                elif progress < 0.7:  # 匀速阶段
                    current_distance = distance * 0.3 + distance * 0.4 * ((progress - 0.3) / 0.4)
                else:  # 减速阶段
                    factor = (progress - 0.7) / 0.3
                    current_distance = distance * 0.7 + distance * 0.3 * (1 - (1 - factor) ** 2)

                # 添加随机抖动
                jitter = random.uniform(-2, 2)
                current_x = start_x + current_distance + jitter
                current_y = start_y + random.uniform(-1, 1)

                await self.browser.page.mouse.move(current_x, current_y)
                await asyncio.sleep(random.uniform(0.01, 0.02))

            # 释放鼠标
            await asyncio.sleep(0.2)
            await self.browser.page.mouse.up()

            logger.info("Slider drag completed")
            await self.browser.random_delay(1, 2)

        except Exception as e:
            logger.error(f"Error dragging slider: {e}", exc_info=True)

    async def _click_login_button(self) -> None:
        """点击登录按钮"""
        logger.info("Clicking login button...")

        login_button_selectors = [
            '#loginsubmit',
            '.login-btn',
            'button:has-text("登录")',
            'a:has-text("登录")',
            '.btn-submit',
        ]

        for selector in login_button_selectors:
            try:
                element = await self.browser.page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )
                if element:
                    # 模拟人类点击
                    box = await element.bounding_box()
                    if box:
                        click_x = box['x'] + box['width'] / 2
                        click_y = box['y'] + box['height'] / 2
                        await self.browser.human_like_mouse_move(int(click_x), int(click_y))

                    await element.click()
                    logger.info("Login button clicked")
                    await self.browser.random_delay(1, 2)
                    return
            except Exception:
                continue

        logger.warning("Login button not found")

    async def _wait_for_login_result(self, timeout: float = 10.0) -> bool:
        """等待登录结果"""
        logger.info("Waiting for login result...")

        try:
            # 等待页面跳转或出现错误提示
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < timeout:
                current_url = self.browser.page.url

                # 检查是否登录成功（跳转到其他页面）
                if 'login' not in current_url.lower():
                    logger.info(f"Login successful, redirected to: {current_url}")
                    return True

                # 检查是否有错误提示
                error_selectors = [
                    '.error-msg',
                    '.err-tip',
                    '.msg-error',
                    ':has-text("用户名或密码错误")',
                    ':has-text("验证码错误")',
                ]

                for selector in error_selectors:
                    try:
                        error_element = await self.browser.page.query_selector(selector)
                        if error_element:
                            error_text = await error_element.text_content()
                            logger.error(f"Login error: {error_text}")
                            return False
                    except Exception:
                        continue

                await asyncio.sleep(0.5)

            # 超时，再次检查URL
            current_url = self.browser.page.url
            if 'login' not in current_url.lower():
                logger.info("Login appears successful")
                return True

            logger.warning("Login result uncertain")
            return False

        except Exception as e:
            logger.error(f"Error waiting for login result: {e}", exc_info=True)
            return False

    async def _save_login_state(self) -> None:
        """保存登录状态（cookies）"""
        try:
            cookies = await self.browser.get_cookies()

            # 保存cookies到文件
            import json
            cookies_file = Path("jd_cookies.json")
            with open(cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)

            logger.info(f"Login state saved to: {cookies_file}")

        except Exception as e:
            logger.error(f"Failed to save login state: {e}")

    async def _save_error_screenshot(self) -> None:
        """保存错误截图"""
        try:
            import time
            screenshot_path = self.screenshot_dir / f"error_{int(time.time())}.png"
            await self.browser.screenshot(str(screenshot_path))
            logger.info(f"Error screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to save error screenshot: {e}")


async def main():
    """主入口函数"""
    jd_login = JDAutoLogin()
    success = await jd_login.login()

    if success:
        print("✅ 京东登录成功！")
        return 0
    else:
        print("❌ 京东登录失败，请检查日志")
        return 1


if __name__ == "__main__":
    import sys
    import random  # 添加这个import，因为_drag_slider使用了random

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
