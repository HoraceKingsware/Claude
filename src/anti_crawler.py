"""
反爬虫策略模块
实现各种反爬虫检测绕过技术
"""
import asyncio
import logging
import random
from typing import Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class AntiCrawlerStrategy:
    """反爬虫策略类"""

    def __init__(self, page: Page):
        self.page = page

    async def inject_fingerprint_spoofing(self) -> None:
        """注入指纹伪装脚本"""
        logger.info("Injecting fingerprint spoofing scripts...")

        # Canvas指纹伪装
        canvas_script = """
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, ...args) {
            const context = originalGetContext.apply(this, [type, ...args]);
            if (type === '2d') {
                const originalFillText = context.fillText;
                context.fillText = function(...args) {
                    // 添加微小随机偏移
                    const noise = Math.random() * 0.0001;
                    args[1] += noise;
                    args[2] += noise;
                    return originalFillText.apply(this, args);
                };
            }
            return context;
        };
        """

        # WebGL指纹伪装
        webgl_script = """
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter.apply(this, [parameter]);
        };
        """

        # AudioContext指纹伪装
        audio_script = """
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            const originalCreateOscillator = AudioContext.prototype.createOscillator;
            AudioContext.prototype.createOscillator = function() {
                const oscillator = originalCreateOscillator.apply(this, arguments);
                const originalStart = oscillator.start;
                oscillator.start = function(...args) {
                    // 添加微小随机延迟
                    const noise = Math.random() * 0.00001;
                    if (args[0] !== undefined) {
                        args[0] += noise;
                    }
                    return originalStart.apply(this, args);
                };
                return oscillator;
            };
        }
        """

        # 字体指纹伪装
        font_script = """
        const originalOffsetWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth');
        const originalOffsetHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');

        Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {
            get: function() {
                const width = originalOffsetWidth.get.call(this);
                return width + (Math.random() > 0.5 ? 1 : 0);
            }
        });

        Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
            get: function() {
                const height = originalOffsetHeight.get.call(this);
                return height + (Math.random() > 0.5 ? 1 : 0);
            }
        });
        """

        await self.page.add_script_tag(content=canvas_script)
        await self.page.add_script_tag(content=webgl_script)
        await self.page.add_script_tag(content=audio_script)
        await self.page.add_script_tag(content=font_script)

        logger.info("Fingerprint spoofing injected successfully")

    async def handle_cookie_consent(self) -> None:
        """处理Cookie同意弹窗"""
        try:
            # 常见的Cookie同意按钮选择器
            consent_selectors = [
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button:has-text("同意")',
                'button:has-text("接受")',
                'button:has-text("确定")',
                'a:has-text("同意")',
                '.cookie-accept',
                '#cookie-accept',
            ]

            for selector in consent_selectors:
                try:
                    element = await self.page.wait_for_selector(
                        selector,
                        timeout=2000,
                        state="visible"
                    )
                    if element:
                        await element.click()
                        logger.info(f"Clicked cookie consent button: {selector}")
                        await asyncio.sleep(1)
                        return
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"No cookie consent found: {e}")

    async def random_mouse_movement(self, duration: float = 2.0) -> None:
        """随机鼠标移动，模拟人类行为"""
        logger.debug("Performing random mouse movements...")

        viewport = self.page.viewport_size
        if not viewport:
            viewport = {"width": 1920, "height": 1080}

        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < duration:
            x = random.randint(100, viewport["width"] - 100)
            y = random.randint(100, viewport["height"] - 100)

            await self.page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))

    async def random_scroll(self) -> None:
        """随机滚动页面"""
        logger.debug("Performing random scroll...")

        # 向下滚动
        scroll_distance = random.randint(100, 500)
        await self.page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        await asyncio.sleep(random.uniform(0.5, 1.5))

        # 向上滚动一点
        scroll_back = random.randint(50, 150)
        await self.page.evaluate(f"window.scrollBy(0, -{scroll_back})")
        await asyncio.sleep(random.uniform(0.3, 0.8))

    async def simulate_reading(self, min_time: float = 2.0, max_time: float = 5.0) -> None:
        """模拟阅读页面"""
        duration = random.uniform(min_time, max_time)
        logger.debug(f"Simulating reading for {duration:.2f}s...")

        # 混合鼠标移动和滚动
        end_time = asyncio.get_event_loop().time() + duration
        while asyncio.get_event_loop().time() < end_time:
            action = random.choice(['move', 'scroll', 'pause'])

            if action == 'move':
                viewport = self.page.viewport_size or {"width": 1920, "height": 1080}
                x = random.randint(200, viewport["width"] - 200)
                y = random.randint(200, viewport["height"] - 200)
                await self.page.mouse.move(x, y)

            elif action == 'scroll':
                scroll = random.randint(-100, 300)
                await self.page.evaluate(f"window.scrollBy(0, {scroll})")

            await asyncio.sleep(random.uniform(0.3, 1.0))

    async def bypass_webdriver_detection(self) -> None:
        """绕过WebDriver检测"""
        logger.info("Bypassing WebDriver detection...")

        script = """
        // 删除 webdriver 属性
        delete Object.getPrototypeOf(navigator).webdriver;

        // 重写 permissions.query
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // 重写 chrome.runtime
        Object.defineProperty(window, 'chrome', {
            get: () => ({
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            })
        });

        // 重写 navigator.plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                },
                {
                    0: {type: "application/pdf", suffixes: "pdf", description: ""},
                    description: "",
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                },
                {
                    0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                    1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"},
                    description: "",
                    filename: "internal-nacl-plugin",
                    length: 2,
                    name: "Native Client"
                }
            ]
        });

        // 重写 navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });

        // 重写 navigator.platform
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });

        // 重写 navigator.hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });

        // 重写 navigator.deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });

        // 伪装 window.outerWidth/outerHeight
        const originalOuterWidth = window.outerWidth;
        const originalOuterHeight = window.outerHeight;
        Object.defineProperty(window, 'outerWidth', {
            get: () => originalOuterWidth || 1920
        });
        Object.defineProperty(window, 'outerHeight', {
            get: () => originalOuterHeight || 1080
        });
        """

        await self.page.add_script_tag(content=script)
        logger.info("WebDriver detection bypass injected")

    async def handle_iframe_detection(self) -> bool:
        """检测并处理iframe（如验证码iframe）"""
        try:
            frames = self.page.frames
            logger.info(f"Found {len(frames)} frames on page")

            # 查找可能的验证码iframe
            for frame in frames:
                frame_url = frame.url
                if any(keyword in frame_url.lower() for keyword in ['captcha', 'verify', 'challenge']):
                    logger.info(f"Found potential captcha iframe: {frame_url}")
                    return True

            return False
        except Exception as e:
            logger.error(f"Error handling iframe detection: {e}")
            return False

    async def wait_for_network_idle(self, timeout: float = 5.0) -> None:
        """等待网络空闲"""
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout * 1000)
            logger.debug("Network is idle")
        except Exception as e:
            logger.debug(f"Network idle timeout: {e}")

    async def clear_browser_cache(self) -> None:
        """清除浏览器缓存"""
        try:
            context = self.page.context
            await context.clear_cookies()
            logger.info("Browser cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    async def detect_and_handle_rate_limit(self) -> bool:
        """检测并处理限流"""
        try:
            # 检查页面内容是否包含限流相关信息
            content = await self.page.content()
            rate_limit_keywords = [
                '访问频繁',
                '请稍后再试',
                'too many requests',
                'rate limit',
                '请求过于频繁',
                '系统繁忙'
            ]

            for keyword in rate_limit_keywords:
                if keyword in content.lower():
                    logger.warning(f"Rate limit detected: {keyword}")
                    # 等待更长时间
                    wait_time = random.uniform(30, 60)
                    logger.info(f"Waiting {wait_time:.2f}s to avoid rate limit...")
                    await asyncio.sleep(wait_time)
                    return True

            return False
        except Exception as e:
            logger.error(f"Error detecting rate limit: {e}")
            return False
