"""
美团自动登录系统
支持AI验证码识别和反爬虫突破
"""

__version__ = "1.0.0"
__author__ = "Auto Login System"

from .meituan_login import MeituanAutoLogin

__all__ = ["MeituanAutoLogin"]
