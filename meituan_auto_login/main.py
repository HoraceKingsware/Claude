"""
美团自动登录 - 主入口文件
"""
import asyncio
import sys
from pathlib import Path
from loguru import logger
from .meituan_login import MeituanAutoLogin


def setup_logger(log_file: str = "./logs/meituan_login.log", level: str = "INFO"):
    """
    配置日志

    Args:
        log_file: 日志文件路径
        level: 日志级别
    """
    # 创建日志目录
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 配置loguru
    logger.remove()  # 移除默认处理器

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )

    # 添加文件输出
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="10 MB",  # 日志文件大小达到10MB时轮转
        retention="30 days",  # 保留30天的日志
        encoding="utf-8"
    )

    logger.info("日志系统已初始化")


async def main():
    """主函数"""
    # 设置日志
    setup_logger()

    logger.info("=" * 60)
    logger.info("美团自动登录系统启动")
    logger.info("=" * 60)

    # 创建登录实例
    auto_login = MeituanAutoLogin(config_path="config.yaml")

    try:
        # 执行登录
        success = await auto_login.login()

        if success:
            logger.info("✓ 登录成功！")
            logger.info("浏览器将保持打开状态，您可以继续使用...")

            # 保持浏览器打开，等待用户操作
            # 可以在这里添加更多自动化操作
            input("\n按Enter键关闭浏览器...")

        else:
            logger.error("✗ 登录失败")
            return 1

    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.exception(f"发生错误: {str(e)}")
        return 1
    finally:
        # 关闭浏览器
        await auto_login.close()

    logger.info("程序结束")
    return 0


def run():
    """运行入口"""
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


if __name__ == "__main__":
    run()
