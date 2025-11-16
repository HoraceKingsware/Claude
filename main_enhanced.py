#!/usr/bin/env python3
"""
京东自动登录 - 增强版主入口
"""
import asyncio
import sys

# 设置事件循环策略（Windows兼容性）
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from src.jd_login_enhanced import main

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
