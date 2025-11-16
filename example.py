"""
美团自动登录 - 使用示例
"""
import asyncio
from meituan_auto_login import MeituanAutoLogin


async def example_basic_login():
    """基础登录示例"""
    print("=== 基础登录示例 ===\n")

    # 创建登录实例（使用配置文件中的账号密码）
    auto_login = MeituanAutoLogin(config_path="config.yaml")

    try:
        # 执行登录
        success = await auto_login.login()

        if success:
            print("✓ 登录成功！")
        else:
            print("✗ 登录失败")

    finally:
        # 关闭浏览器
        await auto_login.close()


async def example_login_with_credentials():
    """使用指定账号密码登录示例"""
    print("=== 指定账号密码登录示例 ===\n")

    # 创建登录实例
    auto_login = MeituanAutoLogin(config_path="config.yaml")

    try:
        # 使用指定的账号密码登录
        username = "your_phone_number"  # 替换为你的手机号
        password = "your_password"      # 替换为你的密码

        success = await auto_login.login(username=username, password=password)

        if success:
            print("✓ 登录成功！")

            # 登录成功后，可以进行其他操作
            # 例如：访问美团的其他页面、获取数据等
            await auto_login.browser.goto("https://www.meituan.com/")

            # 保持浏览器打开
            input("\n按Enter键关闭浏览器...")
        else:
            print("✗ 登录失败")

    finally:
        await auto_login.close()


async def example_with_context_manager():
    """使用上下文管理器的示例"""
    print("=== 使用上下文管理器示例 ===\n")

    # 使用async with自动管理浏览器生命周期
    async with MeituanAutoLogin(config_path="config.yaml") as auto_login:
        success = await auto_login.login()

        if success:
            print("✓ 登录成功！")
            # 执行其他操作...
        else:
            print("✗ 登录失败")

    # 浏览器会自动关闭


async def example_save_and_load_cookies():
    """Cookie保存和加载示例"""
    print("=== Cookie保存和加载示例 ===\n")

    auto_login = MeituanAutoLogin(config_path="config.yaml")

    try:
        # 第一次登录
        print("执行第一次登录...")
        success = await auto_login.login()

        if success:
            print("✓ 第一次登录成功，Cookie已自动保存")

            # Cookie会自动保存到 ./cookies/meituan_cookies.json
            print("Cookie保存路径: ./cookies/meituan_cookies.json")

            # 下次运行时，会自动尝试使用保存的Cookie登录
            print("\n下次运行时，程序会先尝试使用保存的Cookie进行快速登录")

    finally:
        await auto_login.close()


async def example_custom_config():
    """自定义配置示例"""
    print("=== 自定义配置示例 ===\n")

    # 你可以创建自己的配置文件
    auto_login = MeituanAutoLogin(config_path="config.yaml")

    # 配置文件中可以设置：
    # - 浏览器类型（chromium/firefox/webkit）
    # - 是否无头模式
    # - 反爬虫设置
    # - 验证码识别方式
    # - 日志级别
    # 等等...

    try:
        success = await auto_login.login()

        if success:
            print("✓ 登录成功！")
        else:
            print("✗ 登录失败")

    finally:
        await auto_login.close()


def main():
    """主函数"""
    print("美团自动登录 - 使用示例\n")
    print("请选择要运行的示例：")
    print("1. 基础登录")
    print("2. 指定账号密码登录")
    print("3. 使用上下文管理器")
    print("4. Cookie保存和加载")
    print("5. 自定义配置")

    choice = input("\n请输入选项 (1-5): ").strip()

    examples = {
        "1": example_basic_login,
        "2": example_login_with_credentials,
        "3": example_with_context_manager,
        "4": example_save_and_load_cookies,
        "5": example_custom_config,
    }

    example_func = examples.get(choice)

    if example_func:
        print("\n" + "=" * 60)
        asyncio.run(example_func())
        print("=" * 60)
    else:
        print("无效的选项")


if __name__ == "__main__":
    main()
