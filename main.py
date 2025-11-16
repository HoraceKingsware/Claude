#!/usr/bin/env python3
"""
京东自动登录 - 主入口脚本
"""
import asyncio
import sys
from src.jd_login import main

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
