"""
AI验证码识别模块
支持使用Claude、GPT-4V等多模态大模型识别验证码
"""
import base64
import logging
from typing import Optional, Tuple
from pathlib import Path
import anthropic
import openai

from .config import Config

logger = logging.getLogger(__name__)


class CaptchaSolver:
    """AI验证码识别器"""

    def __init__(self):
        self.provider = Config.AI_PROVIDER
        self.api_key = Config.AI_API_KEY
        self.model = Config.AI_MODEL

        if self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == "openai":
            if Config.AI_API_BASE:
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=Config.AI_API_BASE
                )
            else:
                self.client = openai.OpenAI(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def _encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _get_image_media_type(self, image_path: str) -> str:
        """获取图片MIME类型"""
        suffix = Path(image_path).suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return media_types.get(suffix, "image/jpeg")

    async def solve_text_captcha(self, image_path: str) -> Optional[str]:
        """
        识别文字验证码

        Args:
            image_path: 验证码图片路径

        Returns:
            识别出的验证码文字，识别失败返回None
        """
        logger.info(f"Solving text captcha: {image_path}")

        try:
            if self.provider == "anthropic":
                return await self._solve_with_claude(image_path)
            elif self.provider == "openai":
                return await self._solve_with_openai(image_path)
        except Exception as e:
            logger.error(f"Failed to solve captcha: {e}")
            return None

    async def _solve_with_claude(self, image_path: str) -> Optional[str]:
        """使用Claude识别验证码"""
        image_data = self._encode_image(image_path)
        media_type = self._get_image_media_type(image_path)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "这是一个验证码图片。请仔细识别图片中的文字或数字，只返回验证码内容本身，不要包含任何其他说明文字。如果验证码包含字母，请注意区分大小写。",
                        },
                    ],
                }
            ],
        )

        if message.content and len(message.content) > 0:
            result = message.content[0].text.strip()
            logger.info(f"Captcha solved: {result}")
            return result

        return None

    async def _solve_with_openai(self, image_path: str) -> Optional[str]:
        """使用OpenAI识别验证码"""
        image_data = self._encode_image(image_path)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "这是一个验证码图片。请仔细识别图片中的文字或数字，只返回验证码内容本身，不要包含任何其他说明文字。如果验证码包含字母，请注意区分大小写。",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1024,
        )

        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content.strip()
            logger.info(f"Captcha solved: {result}")
            return result

        return None

    async def solve_slider_captcha(self, background_image: str, slider_image: str) -> Optional[int]:
        """
        识别滑块验证码

        Args:
            background_image: 背景图片路径
            slider_image: 滑块图片路径

        Returns:
            滑块需要移动的距离（像素），识别失败返回None
        """
        logger.info(f"Solving slider captcha: {background_image}, {slider_image}")

        try:
            if self.provider == "anthropic":
                return await self._solve_slider_with_claude(background_image, slider_image)
            elif self.provider == "openai":
                return await self._solve_slider_with_openai(background_image, slider_image)
        except Exception as e:
            logger.error(f"Failed to solve slider captcha: {e}")
            return None

    async def _solve_slider_with_claude(self, bg_image: str, slider_image: str) -> Optional[int]:
        """使用Claude识别滑块验证码"""
        bg_data = self._encode_image(bg_image)
        slider_data = self._encode_image(slider_image)
        bg_media_type = self._get_image_media_type(bg_image)
        slider_media_type = self._get_image_media_type(slider_image)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "这是一个滑块验证码。第一张图是背景图，第二张图是滑块图。请分析滑块应该移动到什么位置才能填补背景图中的缺口。只返回一个数字，表示滑块需要向右移动的像素距离。",
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": bg_media_type,
                                "data": bg_data,
                            },
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": slider_media_type,
                                "data": slider_data,
                            },
                        },
                    ],
                }
            ],
        )

        if message.content and len(message.content) > 0:
            result_text = message.content[0].text.strip()
            # 提取数字
            import re
            numbers = re.findall(r'\d+', result_text)
            if numbers:
                distance = int(numbers[0])
                logger.info(f"Slider distance: {distance}px")
                return distance

        return None

    async def _solve_slider_with_openai(self, bg_image: str, slider_image: str) -> Optional[int]:
        """使用OpenAI识别滑块验证码"""
        bg_data = self._encode_image(bg_image)
        slider_data = self._encode_image(slider_image)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "这是一个滑块验证码。第一张图是背景图，第二张图是滑块图。请分析滑块应该移动到什么位置才能填补背景图中的缺口。只返回一个数字，表示滑块需要向右移动的像素距离。",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{bg_data}"
                            },
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{slider_data}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1024,
        )

        if response.choices and len(response.choices) > 0:
            result_text = response.choices[0].message.content.strip()
            # 提取数字
            import re
            numbers = re.findall(r'\d+', result_text)
            if numbers:
                distance = int(numbers[0])
                logger.info(f"Slider distance: {distance}px")
                return distance

        return None

    async def solve_click_captcha(self, image_path: str, instruction: str) -> Optional[list[Tuple[int, int]]]:
        """
        识别点选验证码

        Args:
            image_path: 验证码图片路径
            instruction: 点选指令（例如："请依次点击：马、鸟、狗"）

        Returns:
            点击坐标列表 [(x1, y1), (x2, y2), ...]，识别失败返回None
        """
        logger.info(f"Solving click captcha: {image_path}, instruction: {instruction}")

        try:
            if self.provider == "anthropic":
                return await self._solve_click_with_claude(image_path, instruction)
            elif self.provider == "openai":
                return await self._solve_click_with_openai(image_path, instruction)
        except Exception as e:
            logger.error(f"Failed to solve click captcha: {e}")
            return None

    async def _solve_click_with_claude(self, image_path: str, instruction: str) -> Optional[list[Tuple[int, int]]]:
        """使用Claude识别点选验证码"""
        image_data = self._encode_image(image_path)
        media_type = self._get_image_media_type(image_path)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": f"这是一个点选验证码图片。指令是：{instruction}\n请分析图片，找出需要点击的目标位置。返回格式为：x1,y1;x2,y2;x3,y3 （坐标用分号分隔，只返回坐标数字，不要其他文字）",
                        },
                    ],
                }
            ],
        )

        if message.content and len(message.content) > 0:
            result_text = message.content[0].text.strip()
            # 解析坐标
            coordinates = []
            import re
            pairs = re.findall(r'(\d+)\s*,\s*(\d+)', result_text)
            for x, y in pairs:
                coordinates.append((int(x), int(y)))

            if coordinates:
                logger.info(f"Click coordinates: {coordinates}")
                return coordinates

        return None

    async def _solve_click_with_openai(self, image_path: str, instruction: str) -> Optional[list[Tuple[int, int]]]:
        """使用OpenAI识别点选验证码"""
        image_data = self._encode_image(image_path)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"这是一个点选验证码图片。指令是：{instruction}\n请分析图片，找出需要点击的目标位置。返回格式为：x1,y1;x2,y2;x3,y3 （坐标用分号分隔，只返回坐标数字，不要其他文字）",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1024,
        )

        if response.choices and len(response.choices) > 0:
            result_text = response.choices[0].message.content.strip()
            # 解析坐标
            coordinates = []
            import re
            pairs = re.findall(r'(\d+)\s*,\s*(\d+)', result_text)
            for x, y in pairs:
                coordinates.append((int(x), int(y)))

            if coordinates:
                logger.info(f"Click coordinates: {coordinates}")
                return coordinates

        return None
