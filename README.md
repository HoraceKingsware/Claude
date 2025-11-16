# 美团自动登录系统

🚀 基于AI技术的美团网站自动登录工具，支持智能验证码识别和反爬虫突破。

## ✨ 核心功能

- ✅ **自动登录** - 自动完成美团网站登录流程
- 🤖 **AI验证码识别** - 集成Claude视觉大模型，智能识别各类验证码
- 🛡️ **反爬虫突破** - 多种反爬虫检测绕过技术
- 🍪 **Cookie管理** - 自动保存和加载Cookie，实现快速登录
- 🎭 **人类行为模拟** - 模拟真实用户操作，提高成功率
- 🔧 **灵活配置** - 支持通过YAML配置文件自定义各种参数

## 🎯 技术特点

### 1. AI验证码识别

- 支持**文字验证码**识别
- 支持**滑块验证码**识别
- 支持**点选验证码**识别
- 使用Claude 3.5 Sonnet视觉模型，识别准确率高

### 2. 反爬虫突破技术

- ✅ 隐藏WebDriver特征
- ✅ 随机化User-Agent
- ✅ 浏览器指纹伪装
- ✅ JavaScript环境混淆
- ✅ 人类行为模拟（随机延迟、鼠标轨迹）
- ✅ Canvas指纹防护

### 3. 智能化设计

- 自动检测验证码类型
- 自动重试机制
- Cookie持久化，提升登录速度
- 灵活的错误处理和日志记录

## 📦 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd Claude
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装Playwright浏览器

```bash
playwright install chromium
```

## ⚙️ 配置

### 1. 环境变量配置

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```bash
# 美团账号信息
MEITUAN_USERNAME=your_phone_number
MEITUAN_PASSWORD=your_password

# Claude API密钥（用于验证码识别）
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 2. 配置文件说明

`config.yaml` 文件包含详细的配置选项：

```yaml
# 登录配置
login:
  url: "https://passport.meituan.com/account/unitivelogin"
  username: ""  # 可以在这里直接配置，或使用环境变量
  password: ""

# 浏览器配置
browser:
  type: "chromium"  # chromium, firefox, webkit
  headless: false   # 是否无头模式
  viewport:
    width: 1920
    height: 1080

# 反爬虫配置
anti_crawler:
  stealth_mode: true           # 启用隐身模式
  random_user_agent: true      # 随机User-Agent
  human_behavior: true         # 模拟人类行为
  delay_range:
    min: 1.0
    max: 3.0

# 验证码配置
captcha:
  provider: "claude"  # claude 或 manual
  claude:
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 1024
    temperature: 0
```

## 🚀 使用方法

### 快速开始

```bash
python -m meituan_auto_login.main
```

### Python代码调用

#### 基础用法

```python
import asyncio
from meituan_auto_login import MeituanAutoLogin

async def main():
    # 创建登录实例
    auto_login = MeituanAutoLogin(config_path="config.yaml")

    try:
        # 执行登录
        success = await auto_login.login()

        if success:
            print("登录成功！")
        else:
            print("登录失败")
    finally:
        await auto_login.close()

asyncio.run(main())
```

#### 指定账号密码

```python
async def main():
    auto_login = MeituanAutoLogin()

    try:
        # 使用指定的账号密码登录
        success = await auto_login.login(
            username="13800138000",
            password="your_password"
        )

        if success:
            print("登录成功！")
    finally:
        await auto_login.close()

asyncio.run(main())
```

#### 使用上下文管理器

```python
async def main():
    # 使用async with自动管理浏览器生命周期
    async with MeituanAutoLogin() as auto_login:
        success = await auto_login.login()

        if success:
            print("登录成功！")
            # 继续其他操作...

asyncio.run(main())
```

### 运行示例

项目提供了多个使用示例：

```bash
python example.py
```

## 📁 项目结构

```
Claude/
├── meituan_auto_login/          # 主包
│   ├── __init__.py              # 包初始化
│   ├── main.py                  # 主入口
│   ├── config.py                # 配置管理
│   ├── browser_automation.py   # 浏览器自动化
│   ├── anti_crawler.py          # 反爬虫模块
│   ├── captcha_solver.py        # 验证码识别
│   └── meituan_login.py         # 美团登录逻辑
├── config.yaml                  # 配置文件
├── .env.example                 # 环境变量示例
├── requirements.txt             # Python依赖
├── example.py                   # 使用示例
└── README.md                    # 说明文档
```

## 🔍 核心模块说明

### 1. 浏览器自动化 (browser_automation.py)

提供基础的浏览器操作封装：
- 浏览器启动和配置
- 页面导航和元素操作
- 截图和Cookie管理
- 上下文管理

### 2. 反爬虫突破 (anti_crawler.py)

实现多种反爬虫绕过技术：
- JavaScript特征隐藏
- 人类行为模拟
- 浏览器指纹伪装
- 随机延迟和轨迹模拟

### 3. 验证码识别 (captcha_solver.py)

集成AI大模型进行验证码识别：
- 文字验证码识别
- 滑块验证码识别
- 点选验证码识别
- 支持自定义识别提供商

### 4. 美团登录 (meituan_login.py)

完整的美团登录流程实现：
- 自动检测登录状态
- Cookie快速登录
- 多种验证码处理
- 登录结果验证

## 🛠️ 高级配置

### 使用代理

在 `.env` 文件中配置代理：

```bash
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 切换浏览器

在 `config.yaml` 中修改：

```yaml
browser:
  type: "firefox"  # 或 webkit
```

### 无头模式

适合在服务器上运行：

```yaml
browser:
  headless: true
```

### 手动验证码识别

如果没有Claude API密钥，可以使用手动识别：

```yaml
captcha:
  provider: "manual"
```

## 📊 日志

日志文件保存在 `./logs/meituan_login.log`，包含详细的运行信息。

## ⚠️ 注意事项

1. **仅用于学习研究** - 本项目仅供学习自动化技术和AI应用，请勿用于非法用途
2. **遵守网站规则** - 使用时请遵守美团网站的服务条款和robots.txt
3. **频率控制** - 避免频繁请求，建议添加适当的延迟
4. **账号安全** - 妥善保管账号密码和API密钥，不要泄露
5. **合法使用** - 仅在授权范围内使用，不要用于爬取用户隐私数据

## 🔐 安全建议

- ✅ 使用环境变量存储敏感信息
- ✅ 不要将 `.env` 文件提交到版本控制系统
- ✅ 定期更换密码和API密钥
- ✅ 使用专用测试账号进行开发测试

## 🐛 常见问题

### 1. 安装Playwright失败

```bash
# 设置国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### 2. 验证码识别失败

- 检查Claude API密钥是否正确
- 确认网络连接正常
- 查看日志文件了解详细错误

### 3. 登录失败

- 确认账号密码正确
- 检查是否需要短信验证
- 查看浏览器截图（保存在临时目录）

### 4. Cookie加载失败

- 删除旧的Cookie文件重新登录
- 检查Cookie文件路径是否正确

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 开源协议

MIT License

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 强大的浏览器自动化工具
- [Anthropic Claude](https://www.anthropic.com/) - 优秀的AI视觉模型
- [Loguru](https://github.com/Delgan/loguru) - 优雅的日志库

## 📮 联系方式

如有问题或建议，请提交Issue。

---

**免责声明**: 本项目仅供学习研究使用，使用本项目所造成的一切后果由使用者自行承担。
