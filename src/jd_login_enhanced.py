"""
京东自动登录核心模块 - 增强版
整合浏览器自动化、AI验证码识别、反爬虫策略，实现京东网站自动登录
"""
import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

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


class JDAutoLoginEnhanced:
    """京东自动登录主类 - 增强版"""

    def __init__(self, debug: bool = False):
        self.browser: Optional[BrowserAutomation] = None
        self.captcha_solver: Optional[CaptchaSolver] = None
        self.anti_crawler: Optional[AntiCrawlerStrategy] = None
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.debug = debug or not Config.HEADLESS
        self.login_method = "password"  # password, qr, sms

    async def login(self, method: str = "password") -> bool:
        """
        执行自动登录

        Args:
            method: 登录方式 (password, qr, sms)

        Returns:
            bool: 登录成功返回True，失败返回False
        """
        self.login_method = method
        logger.info(f"Starting JD auto login with method: {method}")

        # 验证配置
        try:
            if method == "password":
                Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return False

        # 初始化组件
        self.browser = BrowserAutomation()
        if method == "password":
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
                    logger.info("✅ Login successful!")
                    return True

                if attempt < Config.MAX_RETRY_TIMES - 1:
                    logger.warning(f"Login failed, retrying in {Config.RETRY_DELAY}s...")
                    await asyncio.sleep(Config.RETRY_DELAY)
                    # 刷新页面重试
                    await self._refresh_page()

            logger.error("❌ All login attempts failed")
            return False

        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return False

        finally:
            # 清理资源
            if self.browser and not self.debug:
                await self.browser.close()
            elif self.debug:
                logger.info("Debug mode: Browser remains open")
                input("Press Enter to close browser...")
                await self.browser.close()

    async def _refresh_page(self) -> None:
        """刷新页面"""
        try:
            logger.info("Refreshing page...")
            await self.browser.page.reload(wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
        except Exception as e:
            logger.warning(f"Page refresh failed: {e}")

    async def _login_attempt(self) -> bool:
        """单次登录尝试"""
        try:
            # 1. 访问登录页面
            await self._navigate_to_login_page()

            # 2. 根据登录方式选择不同流程
            if self.login_method == "qr":
                return await self._qr_login()
            elif self.login_method == "sms":
                return await self._sms_login()
            else:
                return await self._password_login()

        except Exception as e:
            logger.error(f"Login attempt error: {e}", exc_info=True)
            # 保存错误截图
            await self._save_error_screenshot(f"error_{self.login_method}")
            return False

    async def _navigate_to_login_page(self) -> None:
        """访问登录页面"""
        logger.info(f"Navigating to login page: {Config.JD_LOGIN_URL}")

        # 使用更快的加载策略
        await self.browser.navigate(Config.JD_LOGIN_URL, wait_until="domcontentloaded")

        # 等待页面基本元素加载
        await asyncio.sleep(2)

        # 绕过WebDriver检测
        await self.anti_crawler.bypass_webdriver_detection()

        # 注入指纹伪装
        await self.anti_crawler.inject_fingerprint_spoofing()

        # 处理可能的Cookie同意弹窗
        await self.anti_crawler.handle_cookie_consent()

        logger.info("Login page loaded")

        if self.debug:
            await self._save_debug_screenshot("01_page_loaded")

    async def _password_login(self) -> bool:
        """密码登录流程"""
        try:
            # 1. 选择账号密码登录方式
            await self._select_password_login()

            # 2. 等待登录表单加载
            await asyncio.sleep(1)

            if self.debug:
                await self._save_debug_screenshot("02_password_tab_selected")

            # 3. 输入账号密码
            await self._input_credentials()

            if self.debug:
                await self._save_debug_screenshot("03_credentials_input")

            # 4. 检查并处理验证码（在点击登录前）
            has_captcha = await self._check_captcha_before_login()

            if has_captcha:
                logger.info("Detected pre-login captcha, handling...")
                captcha_handled = await self._handle_captcha()
                if not captcha_handled:
                    logger.warning("Failed to handle pre-login captcha")
                    return False

            if self.debug:
                await self._save_debug_screenshot("04_before_login_click")

            # 5. 点击登录按钮
            await self._click_login_button()

            # 6. 等待并处理登录后可能出现的验证码
            await asyncio.sleep(2)

            if self.debug:
                await self._save_debug_screenshot("05_after_login_click")

            # 7. 检查是否需要处理登录后验证码
            post_login_captcha = await self._check_captcha_after_login()

            if post_login_captcha:
                logger.info("Detected post-login captcha, handling...")
                captcha_handled = await self._handle_captcha()
                if not captcha_handled:
                    logger.warning("Failed to handle post-login captcha")
                    return False

            # 8. 等待登录结果
            login_success = await self._wait_for_login_result()

            if login_success:
                # 保存登录状态
                await self._save_login_state()

            return login_success

        except Exception as e:
            logger.error(f"Password login error: {e}", exc_info=True)
            return False

    async def _select_password_login(self) -> None:
        """选择账号密码登录方式"""
        logger.info("Selecting password login method...")

        # 更多可能的选择器
        selectors = [
            '.login-tab-r',
            'a:has-text("账户登录")',
            'a:has-text("账号登录")',
            '.login-tab:has-text("账户")',
            'a[clstag*="password"]',
            '.login-tab:nth-child(2)',
        ]

        for selector in selectors:
            try:
                element = await self.browser.page.wait_for_selector(
                    selector,
                    timeout=3000,
                    state="visible"
                )
                if element:
                    await element.click()
                    logger.info(f"✅ Clicked password login tab: {selector}")
                    await self.browser.random_delay(0.5, 1.0)
                    return
            except Exception as e:
                logger.debug(f"Selector {selector} not found: {e}")
                continue

        logger.warning("Could not find password login tab, assuming already selected")

    async def _input_credentials(self) -> None:
        """输入账号密码"""
        logger.info("Inputting credentials...")

        # 用户名输入框选择器（更全面）
        username_selectors = [
            '#loginname',
            'input[name="loginname"]',
            'input[id*="loginname"]',
            'input[placeholder*="邮箱"]',
            'input[placeholder*="用户名"]',
            'input[placeholder*="手机号"]',
            '.login-form input[type="text"]',
            'input.itxt',
        ]

        # 密码输入框选择器（更全面）
        password_selectors = [
            '#nloginpwd',
            'input[name="nloginpwd"]',
            'input[id*="pwd"]',
            'input[type="password"]',
            'input[placeholder*="密码"]',
            '.login-form input[type="password"]',
            'input.itxt[type="password"]',
        ]

        # 输入用户名
        username_input = False
        for selector in username_selectors:
            try:
                element = await self.browser.page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )
                if element:
                    # 清空输入框
                    await element.fill('')
                    await asyncio.sleep(0.3)

                    # 人类化输入
                    await self.browser.human_like_type(selector, Config.JD_USERNAME)
                    logger.info(f"✅ Username input completed with selector: {selector}")
                    username_input = True
                    break
            except Exception as e:
                logger.debug(f"Username selector {selector} failed: {e}")
                continue

        if not username_input:
            logger.error("❌ Failed to input username")
            raise RuntimeError("Username input failed")

        await self.browser.random_delay(0.3, 0.8)

        # 输入密码
        password_input = False
        for selector in password_selectors:
            try:
                element = await self.browser.page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )
                if element:
                    # 清空输入框
                    await element.fill('')
                    await asyncio.sleep(0.3)

                    # 人类化输入
                    await self.browser.human_like_type(selector, Config.JD_PASSWORD)
                    logger.info(f"✅ Password input completed with selector: {selector}")
                    password_input = True
                    break
            except Exception as e:
                logger.debug(f"Password selector {selector} failed: {e}")
                continue

        if not password_input:
            logger.error("❌ Failed to input password")
            raise RuntimeError("Password input failed")

        await self.browser.random_delay(0.5, 1.0)

    async def _check_captcha_before_login(self) -> bool:
        """检查登录前是否有验证码"""
        logger.info("Checking for pre-login captcha...")

        # 更全面的验证码选择器
        captcha_selectors = [
            '.captcha-img',
            '#JD_Verification1',
            'img[src*="captcha"]',
            'img[src*="verify"]',
            'img[alt*="验证码"]',
            '.JDJRV-slide-bg',  # 滑块验证码
            '#slideBlock',
            '.verification-code',
            'img[id*="authcode"]',
        ]

        for selector in captcha_selectors:
            try:
                element = await self.browser.page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        logger.info(f"✅ Found pre-login captcha: {selector}")
                        return True
            except Exception as e:
                logger.debug(f"Captcha selector {selector} check failed: {e}")
                continue

        logger.info("No pre-login captcha detected")
        return False

    async def _check_captcha_after_login(self) -> bool:
        """检查登录后是否有验证码"""
        logger.info("Checking for post-login captcha...")

        # 等待可能出现的验证码
        await asyncio.sleep(1)

        # 检查验证码相关元素
        captcha_indicators = [
            ':has-text("验证码")',
            ':has-text("滑动验证")',
            ':has-text("图形验证")',
            '.captcha-layer',
            '#divAuthCode',
            '.JDJRV-bigimg',
        ]

        for selector in captcha_indicators:
            try:
                element = await self.browser.page.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    if is_visible:
                        logger.info(f"✅ Found post-login captcha: {selector}")
                        return True
            except Exception:
                continue

        logger.info("No post-login captcha detected")
        return False

    async def _handle_captcha(self) -> bool:
        """处理验证码 - 增强版"""
        logger.info("🔍 Analyzing captcha type...")

        try:
            # 先截图保存
            captcha_screenshot = self.screenshot_dir / f"captcha_debug_{int(time.time())}.png"
            await self.browser.screenshot(str(captcha_screenshot))
            logger.info(f"Captcha screenshot saved: {captcha_screenshot}")

            # 检测滑块验证码
            slider_selectors = [
                '.JDJRV-slide-btn',
                '#slideBlock',
                '.slide-verify-btn',
                'div[id*="nc_"]',  # 网易滑块
            ]

            for selector in slider_selectors:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    logger.info(f"✅ Detected slider captcha: {selector}")
                    return await self._solve_slider_captcha()

            # 检测文字验证码
            text_captcha_selectors = [
                '.captcha-img',
                'img[src*="authcode"]',
                'img[alt*="验证码"]',
            ]

            for selector in text_captcha_selectors:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    logger.info(f"✅ Detected text captcha: {selector}")
                    return await self._solve_text_captcha()

            # 检测点选验证码
            click_captcha_selectors = [
                '.JDJRV-bigimg',
                'canvas[id*="verify"]',
            ]

            for selector in click_captcha_selectors:
                element = await self.browser.page.query_selector(selector)
                if element and await element.is_visible():
                    logger.info(f"✅ Detected click captcha: {selector}")
                    logger.warning("⚠️ Click captcha requires manual intervention")

                    if self.debug or not Config.HEADLESS:
                        logger.info("Please solve the captcha manually...")
                        # 等待用户手动解决
                        await asyncio.sleep(30)
                        return True

                    return False

            logger.warning("⚠️ Unknown captcha type or no captcha found")
            return True  # 假设没有验证码

        except Exception as e:
            logger.error(f"Captcha handling error: {e}", exc_info=True)
            return False

    async def _solve_text_captcha(self) -> bool:
        """处理文字验证码 - 增强版"""
        logger.info("🎯 Solving text captcha...")

        try:
            # 截取验证码图片
            captcha_img_path = self.screenshot_dir / f"captcha_text_{int(time.time())}.png"

            # 查找验证码图片元素
            img_selectors = [
                '.captcha-img',
                'img[src*="authcode"]',
                'img[src*="captcha"]',
                'img[alt*="验证码"]',
            ]

            captcha_img = None
            for selector in img_selectors:
                try:
                    captcha_img = await self.browser.page.wait_for_selector(selector, timeout=3000)
                    if captcha_img and await captcha_img.is_visible():
                        break
                except:
                    continue

            if not captcha_img:
                logger.error("❌ Captcha image not found")
                return False

            # 截图
            await captcha_img.screenshot(path=str(captcha_img_path))
            logger.info(f"Captcha screenshot saved: {captcha_img_path}")

            # 使用AI识别验证码
            captcha_text = await self.captcha_solver.solve_text_captcha(str(captcha_img_path))

            if not captcha_text:
                logger.error("❌ Failed to solve captcha")
                return False

            logger.info(f"✅ Captcha solved: {captcha_text}")

            # 输入验证码
            input_selectors = [
                '#authcode',
                'input[name="authcode"]',
                'input[id*="authcode"]',
                '.captcha-input',
                'input[placeholder*="验证码"]',
            ]

            for selector in input_selectors:
                try:
                    element = await self.browser.page.wait_for_selector(
                        selector,
                        timeout=3000,
                        state="visible"
                    )
                    if element:
                        await element.fill(captcha_text)
                        logger.info(f"✅ Captcha input completed: {selector}")
                        await self.browser.random_delay(0.5, 1.0)
                        return True
                except:
                    continue

            logger.error("❌ Captcha input field not found")
            return False

        except Exception as e:
            logger.error(f"Text captcha error: {e}", exc_info=True)
            return False

    async def _solve_slider_captcha(self) -> bool:
        """处理滑块验证码 - 增强版"""
        logger.info("🎯 Solving slider captcha...")

        try:
            # 等待滑块完全加载
            await asyncio.sleep(2)

            # 查找滑块按钮
            slider_button_selectors = [
                '.JDJRV-slide-btn',
                '#slideBlock',
                '.slide-verify-btn',
                'div[id*="nc_1_n1z"]',
            ]

            slider_button = None
            for selector in slider_button_selectors:
                try:
                    slider_button = await self.browser.page.wait_for_selector(selector, timeout=3000)
                    if slider_button and await slider_button.is_visible():
                        logger.info(f"✅ Found slider button: {selector}")
                        break
                except:
                    continue

            if not slider_button:
                logger.error("❌ Slider button not found")

                # 如果是有头模式，提示手动操作
                if self.debug or not Config.HEADLESS:
                    logger.info("⚠️ Please solve the slider captcha manually...")
                    logger.info("Waiting 30 seconds for manual intervention...")
                    await asyncio.sleep(30)
                    return True

                return False

            # 截取背景图和滑块图（如果需要AI识别）
            # 这里先尝试简单的滑动策略

            # 获取滑块位置
            box = await slider_button.bounding_box()
            if not box:
                logger.error("❌ Failed to get slider bounding box")
                return False

            # 计算滑动距离（通常滑到最右边）
            # 可以使用AI识别更精确的距离，这里先用固定距离
            distance = 260  # 典型的滑块距离

            logger.info(f"Attempting to drag slider {distance}px...")

            # 执行拖动
            await self._drag_slider_enhanced(slider_button, distance)

            # 等待验证结果
            await asyncio.sleep(2)

            # 检查是否验证成功
            # 通常成功后滑块会消失或显示成功标志
            is_still_visible = await slider_button.is_visible()

            if not is_still_visible:
                logger.info("✅ Slider captcha solved successfully")
                return True
            else:
                logger.warning("⚠️ Slider captcha may have failed, checking...")

                # 检查错误提示
                error_selectors = [
                    ':has-text("验证失败")',
                    ':has-text("请重试")',
                    '.JDJRV-slide-tips',
                ]

                for selector in error_selectors:
                    try:
                        error_elem = await self.browser.page.query_selector(selector)
                        if error_elem and await error_elem.is_visible():
                            error_text = await error_elem.text_content()
                            logger.warning(f"Slider verification error: {error_text}")
                            return False
                    except:
                        continue

                # 没有明确错误，假设成功
                return True

        except Exception as e:
            logger.error(f"Slider captcha error: {e}", exc_info=True)
            return False

    async def _drag_slider_enhanced(self, slider_button, distance: int) -> None:
        """增强版滑块拖动 - 更自然的轨迹"""
        import random

        logger.info(f"Dragging slider {distance}px with enhanced trajectory...")

        try:
            box = await slider_button.bounding_box()
            if not box:
                logger.error("Failed to get slider bounding box")
                return

            start_x = box['x'] + box['width'] / 2
            start_y = box['y'] + box['height'] / 2

            # 移动到滑块
            await self.browser.page.mouse.move(start_x, start_y)
            await asyncio.sleep(random.uniform(0.1, 0.3))

            # 按下鼠标
            await self.browser.page.mouse.down()
            await asyncio.sleep(random.uniform(0.05, 0.15))

            # 生成更真实的轨迹：快速移动 -> 减速 -> 微调
            steps = random.randint(25, 40)
            moved_distance = 0

            # 第一阶段：快速移动到目标附近（90%）
            phase1_distance = distance * 0.9
            phase1_steps = int(steps * 0.6)

            for i in range(phase1_steps):
                progress = (i + 1) / phase1_steps
                # 加速曲线
                current_distance = phase1_distance * (1 - (1 - progress) ** 2)

                # 添加随机抖动
                jitter_x = random.uniform(-1.5, 1.5)
                jitter_y = random.uniform(-0.5, 0.5)

                current_x = start_x + current_distance + jitter_x
                current_y = start_y + jitter_y

                await self.browser.page.mouse.move(current_x, current_y)
                await asyncio.sleep(random.uniform(0.008, 0.015))

            moved_distance = phase1_distance

            # 第二阶段：减速移动到精确位置
            phase2_distance = distance - moved_distance
            phase2_steps = steps - phase1_steps

            for i in range(phase2_steps):
                progress = (i + 1) / phase2_steps
                # 减速曲线
                current_distance = moved_distance + phase2_distance * progress

                jitter_x = random.uniform(-0.5, 0.5)
                jitter_y = random.uniform(-0.3, 0.3)

                current_x = start_x + current_distance + jitter_x
                current_y = start_y + jitter_y

                await self.browser.page.mouse.move(current_x, current_y)
                await asyncio.sleep(random.uniform(0.015, 0.030))

            # 第三阶段：微调（模拟人类的小幅修正）
            for _ in range(random.randint(2, 5)):
                micro_adjust = random.uniform(-2, 2)
                current_x = start_x + distance + micro_adjust
                current_y = start_y + random.uniform(-0.5, 0.5)

                await self.browser.page.mouse.move(current_x, current_y)
                await asyncio.sleep(random.uniform(0.020, 0.040))

            # 短暂停留，模拟人类确认
            await asyncio.sleep(random.uniform(0.1, 0.3))

            # 释放鼠标
            await self.browser.page.mouse.up()

            logger.info("Slider drag completed with enhanced trajectory")

        except Exception as e:
            logger.error(f"Enhanced drag error: {e}", exc_info=True)

    async def _click_login_button(self) -> None:
        """点击登录按钮 - 增强版"""
        logger.info("Clicking login button...")

        login_button_selectors = [
            '#loginsubmit',
            '.login-btn',
            'button:has-text("登录")',
            'a:has-text("登 录")',
            '.btn-submit',
            'div.login-btn',
            'a[clstag*="login"]',
            'button[type="submit"]',
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
                    logger.info(f"✅ Login button clicked: {selector}")
                    await self.browser.random_delay(0.5, 1.5)
                    return
            except Exception as e:
                logger.debug(f"Login button selector {selector} failed: {e}")
                continue

        logger.warning("⚠️ Login button not found, trying Enter key...")

        # 尝试按回车键
        try:
            await self.browser.page.keyboard.press('Enter')
            logger.info("✅ Pressed Enter key")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"❌ Failed to press Enter: {e}")

    async def _wait_for_login_result(self, timeout: float = 15.0) -> bool:
        """等待登录结果 - 增强版"""
        logger.info("Waiting for login result...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                current_url = self.browser.page.url
                logger.debug(f"Current URL: {current_url}")

                # 检查是否登录成功（跳转到其他页面）
                success_indicators = [
                    'www.jd.com',
                    'home.jd.com',
                    'i.jd.com',
                ]

                for indicator in success_indicators:
                    if indicator in current_url.lower() and 'login' not in current_url.lower():
                        logger.info(f"✅ Login successful! Redirected to: {current_url}")
                        return True

                # 检查是否有成功标识
                success_selectors = [
                    '.nickname',
                    '#ttbar-login',
                    '.user-info',
                ]

                for selector in success_selectors:
                    try:
                        element = await self.browser.page.query_selector(selector)
                        if element and await element.is_visible():
                            logger.info(f"✅ Login successful! Found element: {selector}")
                            return True
                    except:
                        continue

                # 检查是否有错误提示
                error_selectors = [
                    '.error-msg',
                    '.err-tip',
                    '.msg-error',
                    ':has-text("用户名或密码错误")',
                    ':has-text("账号或密码不正确")',
                    ':has-text("验证码错误")',
                    ':has-text("验证码校验失败")',
                    ':has-text("登录失败")',
                ]

                for selector in error_selectors:
                    try:
                        error_element = await self.browser.page.query_selector(selector)
                        if error_element and await error_element.is_visible():
                            error_text = await error_element.text_content()
                            logger.error(f"❌ Login error: {error_text}")
                            return False
                    except:
                        continue

                await asyncio.sleep(0.5)

            except Exception as e:
                logger.debug(f"Error checking login result: {e}")
                await asyncio.sleep(0.5)

        # 超时，再次检查URL
        try:
            current_url = self.browser.page.url
            if 'login' not in current_url.lower():
                logger.info("✅ Login appears successful (no longer on login page)")
                return True
        except:
            pass

        logger.warning("⚠️ Login result uncertain after timeout")
        return False

    async def _qr_login(self) -> bool:
        """二维码登录"""
        logger.info("🔍 Attempting QR code login...")

        try:
            # 切换到扫码登录
            qr_tab_selectors = [
                '.login-tab-l',
                'a:has-text("扫码登录")',
                'a:has-text("二维码登录")',
            ]

            for selector in qr_tab_selectors:
                try:
                    element = await self.browser.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        await element.click()
                        logger.info(f"✅ Switched to QR login: {selector}")
                        break
                except:
                    continue

            await asyncio.sleep(2)

            # 查找二维码
            qr_selectors = [
                '.qrcode-img',
                'img[src*="qrcode"]',
                '#qrcode',
            ]

            qr_found = False
            for selector in qr_selectors:
                try:
                    qr_elem = await self.browser.page.query_selector(selector)
                    if qr_elem and await qr_elem.is_visible():
                        logger.info(f"✅ QR code found: {selector}")
                        qr_found = True

                        # 保存二维码
                        qr_path = self.screenshot_dir / f"qrcode_{int(time.time())}.png"
                        await qr_elem.screenshot(path=str(qr_path))
                        logger.info(f"📱 QR code saved to: {qr_path}")
                        logger.info("📱 Please scan the QR code with your JD app...")

                        break
                except:
                    continue

            if not qr_found:
                logger.error("❌ QR code not found")
                return False

            # 等待扫码（最多2分钟）
            logger.info("⏳ Waiting for QR code scan (up to 120s)...")

            return await self._wait_for_login_result(timeout=120.0)

        except Exception as e:
            logger.error(f"QR login error: {e}", exc_info=True)
            return False

    async def _sms_login(self) -> bool:
        """短信验证码登录"""
        logger.info("🔍 SMS login not fully implemented yet")
        logger.info("💡 Please use password or QR login instead")
        return False

    async def _save_login_state(self) -> None:
        """保存登录状态（cookies）"""
        try:
            cookies = await self.browser.get_cookies()

            # 保存cookies到文件
            import json
            cookies_file = Path("jd_cookies.json")
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Login state saved to: {cookies_file}")

        except Exception as e:
            logger.error(f"Failed to save login state: {e}")

    async def _save_error_screenshot(self, prefix: str = "error") -> None:
        """保存错误截图"""
        try:
            screenshot_path = self.screenshot_dir / f"{prefix}_{int(time.time())}.png"
            await self.browser.screenshot(str(screenshot_path))
            logger.info(f"📸 Error screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to save error screenshot: {e}")

    async def _save_debug_screenshot(self, name: str) -> None:
        """保存调试截图"""
        if not self.debug:
            return

        try:
            screenshot_path = self.screenshot_dir / f"debug_{name}_{int(time.time())}.png"
            await self.browser.screenshot(str(screenshot_path))
            logger.debug(f"📸 Debug screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.debug(f"Failed to save debug screenshot: {e}")


async def main():
    """主入口函数"""
    import sys
    import random  # 添加这个import

    # 检查命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='JD Auto Login - Enhanced')
    parser.add_argument('--method', choices=['password', 'qr', 'sms'], default='password',
                        help='Login method (default: password)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    print("=" * 60)
    print("京东自动登录 - 增强版")
    print("=" * 60)
    print(f"登录方式: {args.method}")
    print(f"调试模式: {'开启' if args.debug else '关闭'}")
    print("=" * 60)

    jd_login = JDAutoLoginEnhanced(debug=args.debug)
    success = await jd_login.login(method=args.method)

    if success:
        print("\n" + "=" * 60)
        print("✅ 京东登录成功！")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ 京东登录失败，请检查日志")
        print("=" * 60)
        print("\n💡 建议:")
        print("  1. 检查用户名和密码是否正确")
        print("  2. 查看日志文件: jd_login.log")
        print("  3. 查看截图: screenshots/ 目录")
        print("  4. 尝试使用二维码登录: python main.py --method qr")
        print("  5. 开启调试模式: python main.py --debug")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    import sys
    import random

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
