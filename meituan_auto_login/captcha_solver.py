"""
验证码识别模块
集成Claude视觉大模型进行验证码识别
"""
import base64
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from io import BytesIO
from PIL import Image
from anthropic import Anthropic
from loguru import logger


class CaptchaSolver:
    """验证码识别类"""

    def __init__(self, config):
        """
        初始化验证码识别器

        Args:
            config: 配置对象
        """
        self.config = config
        self.provider = config.captcha_provider

        if self.provider == 'claude':
            claude_config = config.claude_config
            api_key = claude_config.get('api_key')
            if not api_key:
                raise ValueError("未配置Claude API密钥，请在环境变量中设置ANTHROPIC_API_KEY")

            self.client = Anthropic(api_key=api_key)
            self.model = claude_config.get('model', 'claude-3-5-sonnet-20241022')
            self.max_tokens = claude_config.get('max_tokens', 1024)
            self.temperature = claude_config.get('temperature', 0)

    async def solve_captcha(self, image_data: bytes, captcha_type: str = "text") -> Optional[str]:
        """
        识别验证码

        Args:
            image_data: 验证码图片数据（字节）
            captcha_type: 验证码类型 (text: 文字验证码, slide: 滑块验证码, click: 点选验证码)

        Returns:
            识别结果文本，失败返回None
        """
        if self.provider == 'claude':
            return await self._solve_with_claude(image_data, captcha_type)
        elif self.provider == 'manual':
            return await self._solve_manually(image_data)
        else:
            logger.error(f"不支持的验证码识别提供商: {self.provider}")
            return None

    async def _solve_with_claude(self, image_data: bytes, captcha_type: str) -> Optional[str]:
        """
        使用Claude识别验证码

        Args:
            image_data: 图片数据
            captcha_type: 验证码类型

        Returns:
            识别结果
        """
        try:
            # 将图片转换为base64
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # 根据验证码类型构造不同的提示词
            prompts = {
                "text": "这是一个文字验证码图片。请识别图片中的所有字符，包括字母和数字。只需要返回识别出的字符，不要添加任何其他说明。字符区分大小写。",
                "slide": "这是一个滑块验证码的缺口图片。请分析缺口的位置，返回缺口距离图片左边缘的像素距离（只返回数字）。",
                "click": "这是一个点选验证码图片。图片中会标注需要点击的文字，请识别这些文字的坐标位置。返回格式：x1,y1;x2,y2;x3,y3",
                "math": "这是一个数学运算验证码。请计算图片中显示的数学表达式的结果。只返回计算结果的数字，不要返回计算过程。",
                "chinese": "这是一个中文验证码图片。请识别图片中的所有中文字符。只需要返回识别出的汉字，不要添加任何其他说明。"
            }

            prompt = prompts.get(captcha_type, prompts["text"])

            # 调用Claude API
            logger.info(f"正在使用Claude识别验证码，类型: {captcha_type}")

            # 使用同步方式调用，但在async函数中用executor运行
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": base64_image,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ],
                        }
                    ],
                )
            )

            # 提取识别结果
            result = response.content[0].text.strip()
            logger.info(f"验证码识别成功: {result}")
            return result

        except Exception as e:
            logger.error(f"Claude识别验证码失败: {str(e)}")
            return None

    async def _solve_manually(self, image_data: bytes) -> Optional[str]:
        """
        手动输入验证码

        Args:
            image_data: 图片数据

        Returns:
            用户输入的验证码
        """
        # 保存验证码图片到临时文件
        temp_path = Path("./temp_captcha.png")
        with open(temp_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"验证码已保存到: {temp_path}")
        print(f"\n请查看验证码图片: {temp_path}")

        # 等待用户输入
        result = input("请输入验证码: ").strip()

        # 删除临时文件
        try:
            temp_path.unlink()
        except:
            pass

        return result if result else None

    async def solve_slide_captcha(
        self,
        background_image: bytes,
        slider_image: bytes
    ) -> Optional[int]:
        """
        识别滑块验证码的滑动距离

        Args:
            background_image: 背景图片数据
            slider_image: 滑块图片数据

        Returns:
            滑动距离（像素），失败返回None
        """
        if self.provider == 'claude':
            try:
                # 将背景图和滑块图拼接
                bg_img = Image.open(BytesIO(background_image))
                slider_img = Image.open(BytesIO(slider_image))

                # 创建一个新图片，将两张图片上下拼接
                total_height = bg_img.height + slider_img.height
                merged_img = Image.new('RGB', (bg_img.width, total_height))
                merged_img.paste(bg_img, (0, 0))
                merged_img.paste(slider_img, (0, bg_img.height))

                # 转换为字节
                img_byte_arr = BytesIO()
                merged_img.save(img_byte_arr, format='PNG')
                merged_image_data = img_byte_arr.getvalue()

                # 使用Claude识别
                result = await self._solve_with_claude(merged_image_data, "slide")
                if result and result.isdigit():
                    return int(result)

            except Exception as e:
                logger.error(f"滑块验证码识别失败: {str(e)}")

        return None

    async def solve_with_retry(
        self,
        image_data: bytes,
        captcha_type: str = "text",
        max_retries: int = None
    ) -> Optional[str]:
        """
        带重试的验证码识别

        Args:
            image_data: 图片数据
            captcha_type: 验证码类型
            max_retries: 最大重试次数

        Returns:
            识别结果
        """
        if max_retries is None:
            max_retries = self.config.get('captcha', 'max_retries', default=3)

        for attempt in range(max_retries):
            logger.info(f"验证码识别尝试 {attempt + 1}/{max_retries}")
            result = await self.solve_captcha(image_data, captcha_type)

            if result:
                return result

            if attempt < max_retries - 1:
                logger.warning(f"识别失败，{2}秒后重试...")
                await asyncio.sleep(2)

        logger.error(f"验证码识别失败，已达到最大重试次数: {max_retries}")
        return None
