"""
配置管理模块
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """京东自动登录配置"""

    # 京东账号配置
    JD_USERNAME: str = os.getenv("JD_USERNAME", "")
    JD_PASSWORD: str = os.getenv("JD_PASSWORD", "")

    # 浏览器配置
    HEADLESS: bool = os.getenv("HEADLESS", "False").lower() == "true"
    BROWSER_TYPE: str = os.getenv("BROWSER_TYPE", "chrome")  # chrome, firefox, edge
    USER_DATA_DIR: Optional[str] = os.getenv("USER_DATA_DIR", None)

    # AI大模型配置 (用于验证码识别)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "anthropic")  # anthropic, openai, custom
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "claude-3-5-sonnet-20241022")
    AI_API_BASE: Optional[str] = os.getenv("AI_API_BASE", None)

    # 反爬虫配置
    ENABLE_STEALTH: bool = os.getenv("ENABLE_STEALTH", "True").lower() == "true"
    RANDOM_DELAY_MIN: float = float(os.getenv("RANDOM_DELAY_MIN", "1.0"))
    RANDOM_DELAY_MAX: float = float(os.getenv("RANDOM_DELAY_MAX", "3.0"))

    # 重试配置
    MAX_RETRY_TIMES: int = int(os.getenv("MAX_RETRY_TIMES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "2.0"))

    # 超时配置
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))
    ELEMENT_WAIT_TIMEOUT: int = int(os.getenv("ELEMENT_WAIT_TIMEOUT", "10"))

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "jd_login.log")

    # 京东登录URL
    JD_LOGIN_URL: str = "https://passport.jd.com/new/login.aspx"

    @classmethod
    def validate(cls) -> bool:
        """验证必需的配置项"""
        if not cls.JD_USERNAME or not cls.JD_PASSWORD:
            raise ValueError("JD_USERNAME and JD_PASSWORD are required")

        if not cls.AI_API_KEY:
            raise ValueError("AI_API_KEY is required for captcha solving")

        return True
