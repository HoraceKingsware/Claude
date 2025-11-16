#!/usr/bin/env python3
"""
快速测试脚本 - 验证所有依赖是否正常工作
"""

def test_imports():
    """测试所有必需的导入"""
    print("🔍 测试Python包导入...")

    try:
        import playwright
        print("  ✅ playwright 导入成功")
    except ImportError as e:
        print(f"  ❌ playwright 导入失败: {e}")
        return False

    try:
        import anthropic
        print("  ✅ anthropic 导入成功")
    except ImportError as e:
        print(f"  ❌ anthropic 导入失败: {e}")
        return False

    try:
        import openai
        print("  ✅ openai 导入成功")
    except ImportError as e:
        print(f"  ❌ openai 导入失败: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv 导入成功")
    except ImportError as e:
        print(f"  ❌ python-dotenv 导入失败: {e}")
        return False

    try:
        import greenlet
        print("  ✅ greenlet 导入成功")
    except ImportError as e:
        print(f"  ❌ greenlet 导入失败: {e}")
        return False

    return True


def test_project_structure():
    """测试项目结构"""
    import os
    print("\n🔍 检查项目结构...")

    required_files = [
        'src/config.py',
        'src/browser_automation.py',
        'src/captcha_solver.py',
        'src/anti_crawler.py',
        'src/jd_login.py',
        'requirements.txt',
        '.env.example',
        'main.py',
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} 缺失")
            all_exist = False

    return all_exist


def test_module_import():
    """测试项目模块导入"""
    print("\n🔍 测试项目模块导入...")

    try:
        from src.config import Config
        print("  ✅ Config 模块导入成功")
    except Exception as e:
        print(f"  ❌ Config 模块导入失败: {e}")
        return False

    try:
        from src.browser_automation import BrowserAutomation
        print("  ✅ BrowserAutomation 模块导入成功")
    except Exception as e:
        print(f"  ❌ BrowserAutomation 模块导入失败: {e}")
        return False

    try:
        from src.captcha_solver import CaptchaSolver
        print("  ✅ CaptchaSolver 模块导入成功")
    except Exception as e:
        print(f"  ❌ CaptchaSolver 模块导入失败: {e}")
        return False

    try:
        from src.anti_crawler import AntiCrawlerStrategy
        print("  ✅ AntiCrawlerStrategy 模块导入成功")
    except Exception as e:
        print(f"  ❌ AntiCrawlerStrategy 模块导入失败: {e}")
        return False

    try:
        from src.jd_login import JDAutoLogin
        print("  ✅ JDAutoLogin 模块导入成功")
    except Exception as e:
        print(f"  ❌ JDAutoLogin 模块导入失败: {e}")
        return False

    return True


def check_env_file():
    """检查环境变量配置"""
    import os
    print("\n🔍 检查环境变量配置...")

    if os.path.exists('.env'):
        print("  ✅ .env 文件存在")
        print("  ⚠️  请确保已配置以下必需项:")
        print("     - JD_USERNAME (京东用户名)")
        print("     - JD_PASSWORD (京东密码)")
        print("     - AI_API_KEY (AI API密钥)")
    else:
        print("  ⚠️  .env 文件不存在")
        print("  📝 请执行: cp .env.example .env")
        print("  📝 然后编辑 .env 文件，填入你的配置")


def main():
    print("=" * 60)
    print("京东自动登录 - 环境测试")
    print("=" * 60)

    # 测试导入
    if not test_imports():
        print("\n❌ 依赖包导入测试失败")
        return 1

    # 测试项目结构
    if not test_project_structure():
        print("\n❌ 项目结构检查失败")
        return 1

    # 测试模块导入
    if not test_module_import():
        print("\n❌ 项目模块导入测试失败")
        return 1

    # 检查环境变量
    check_env_file()

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！环境配置正常")
    print("=" * 60)
    print("\n📖 下一步:")
    print("  1. 配置环境变量: cp .env.example .env && vim .env")
    print("  2. 运行程序: python main.py")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
