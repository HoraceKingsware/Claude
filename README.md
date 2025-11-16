# 京东自动登录 (JD Auto Login)

基于AI大模型的京东网站自动登录工具，支持智能验证码识别和反爬虫检测绕过。

## 功能特性

- **智能验证码识别**：使用Claude/GPT-4V等多模态大模型识别各类验证码
  - 文字验证码
  - 滑块验证码
  - 点选验证码

- **反爬虫检测绕过**：多重技术突破网站限制
  - WebDriver特征隐藏
  - 浏览器指纹伪装 (Canvas, WebGL, AudioContext等)
  - 人类化操作模拟 (鼠标轨迹、输入速度、随机延迟)
  - User-Agent随机化

- **浏览器自动化**：基于Playwright实现
  - 支持Chrome/Firefox/Edge
  - 无头/有头模式切换
  - Cookie状态保存

- **智能重试机制**：登录失败自动重试
- **详细日志记录**：完整的操作日志和错误截图

## 技术架构

```
京东自动登录系统
├── 浏览器自动化模块 (browser_automation.py)
│   ├── Playwright驱动
│   ├── 人类化操作模拟
│   └── 反检测脚本注入
├── AI验证码识别模块 (captcha_solver.py)
│   ├── Claude/GPT-4V集成
│   ├── 文字验证码识别
│   ├── 滑块验证码识别
│   └── 点选验证码识别
├── 反爬虫策略模块 (anti_crawler.py)
│   ├── 指纹伪装
│   ├── WebDriver检测绕过
│   └── 行为模拟
└── 登录核心模块 (jd_login.py)
    ├── 登录流程编排
    ├── 重试机制
    └── 状态保存
```

## 安装部署

### 1. 环境要求

- Python 3.8+
- 稳定的网络连接
- AI API密钥 (Claude或OpenAI)

### 2. 安装依赖

```bash
# 克隆或下载项目
cd jd-auto-login

# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
# 或者安装所有浏览器
playwright install
```

### 3. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件，填入你的信息
vim .env
```

必需配置项：
```bash
JD_USERNAME=your_jd_username      # 京东用户名/邮箱/手机号
JD_PASSWORD=your_jd_password      # 京东密码
AI_API_KEY=your_api_key_here      # AI API密钥
```

可选配置项：
```bash
HEADLESS=False                    # 是否无头模式
BROWSER_TYPE=chrome               # 浏览器类型
AI_PROVIDER=anthropic             # AI提供商 (anthropic/openai)
AI_MODEL=claude-3-5-sonnet-20241022  # AI模型
LOG_LEVEL=INFO                    # 日志级别
```

## 使用方法

### 基本使用

```bash
# 直接运行
python main.py

# 或者作为模块运行
python -m src.jd_login
```

### Python代码调用

```python
import asyncio
from src.jd_login import JDAutoLogin

async def login():
    jd = JDAutoLogin()
    success = await jd.login()

    if success:
        print("登录成功！")
    else:
        print("登录失败")

asyncio.run(login())
```

### 命令行选项

```bash
# 查看日志
tail -f jd_login.log

# 查看错误截图
ls screenshots/
```

## 配置说明

### AI提供商配置

#### 使用Claude (推荐)

```bash
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-xxx
AI_MODEL=claude-3-5-sonnet-20241022
```

#### 使用OpenAI

```bash
AI_PROVIDER=openai
AI_API_KEY=sk-xxx
AI_MODEL=gpt-4-vision-preview
# AI_API_BASE=https://api.openai.com/v1  # 可选
```

### 浏览器配置

```bash
# 无头模式（后台运行，不显示浏览器窗口）
HEADLESS=True

# 有头模式（显示浏览器窗口，方便调试）
HEADLESS=False

# 浏览器类型
BROWSER_TYPE=chrome    # chrome, firefox, webkit
```

### 反爬虫配置

```bash
# 启用反检测
ENABLE_STEALTH=True

# 操作延迟范围（秒）
RANDOM_DELAY_MIN=1.0
RANDOM_DELAY_MAX=3.0

# 重试配置
MAX_RETRY_TIMES=3
RETRY_DELAY=2.0
```

## 工作原理

### 登录流程

1. **初始化浏览器**
   - 启动Playwright浏览器
   - 注入反检测脚本
   - 配置浏览器指纹

2. **访问登录页面**
   - 导航到京东登录页
   - 处理Cookie同意弹窗
   - 模拟人类浏览行为

3. **输入凭证**
   - 选择账号密码登录方式
   - 人类化输入用户名和密码
   - 添加随机延迟

4. **处理验证码**
   - 检测验证码类型
   - 截取验证码图片
   - 调用AI模型识别
   - 自动输入或拖动

5. **提交登录**
   - 点击登录按钮
   - 等待登录结果
   - 保存登录状态

6. **状态保存**
   - 保存Cookies到文件
   - 后续可直接使用登录状态

### 反爬虫技术

#### 1. WebDriver特征隐藏
- 移除`navigator.webdriver`属性
- 伪装`chrome.runtime`对象
- 修改`permissions.query`行为

#### 2. 浏览器指纹伪装
- **Canvas指纹**：添加微小随机噪点
- **WebGL指纹**：伪装GPU信息
- **AudioContext指纹**：修改音频特征
- **字体指纹**：随机化元素尺寸

#### 3. 人类化行为模拟
- **鼠标轨迹**：贝塞尔曲线模拟真实移动
- **输入速度**：随机延迟，模拟打字
- **随机滚动**：模拟阅读页面
- **操作延迟**：所有操作都有随机延迟

#### 4. 其他技术
- User-Agent随机化
- 时区和地理位置设置
- 网络空闲检测
- 限流检测与处理

### 验证码识别

使用多模态大模型（Claude 3.5 Sonnet / GPT-4V）识别验证码：

- **文字验证码**：直接识别图片中的文字/数字
- **滑块验证码**：分析缺口位置，计算滑动距离
- **点选验证码**：识别目标物体，返回点击坐标

## 注意事项

### 安全提示

1. **保护API密钥**：不要将`.env`文件提交到版本控制
2. **保护账号密码**：使用环境变量，不要硬编码
3. **合理使用**：避免过于频繁的登录请求
4. **遵守规则**：仅用于个人账号的自动登录

### 使用限制

1. **京东可能更新登录流程**，需要相应调整代码
2. **AI识别不是100%准确**，可能需要重试
3. **部分高级反爬虫可能无法绕过**
4. **需要稳定的网络环境**

### 故障排查

#### 1. 登录失败

- 检查用户名密码是否正确
- 查看日志文件 `jd_login.log`
- 查看错误截图 `screenshots/`
- 尝试有头模式调试 `HEADLESS=False`

#### 2. 验证码识别失败

- 检查AI API密钥是否正确
- 检查网络连接是否稳定
- 尝试切换AI提供商
- 查看验证码截图是否清晰

#### 3. 浏览器启动失败

- 确认已安装Playwright浏览器：`playwright install`
- 检查系统依赖：`playwright install-deps`
- 尝试切换浏览器类型

#### 4. 反爬虫检测

- 启用反检测：`ENABLE_STEALTH=True`
- 增加操作延迟：调大 `RANDOM_DELAY_MAX`
- 使用真实浏览器配置文件：设置 `USER_DATA_DIR`

## 项目结构

```
jd-auto-login/
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── browser_automation.py  # 浏览器自动化
│   ├── captcha_solver.py      # AI验证码识别
│   ├── anti_crawler.py        # 反爬虫策略
│   └── jd_login.py            # 登录核心逻辑
├── screenshots/               # 截图保存目录
├── .env.example              # 环境变量示例
├── requirements.txt          # Python依赖
├── main.py                   # 主入口脚本
├── jd_cookies.json           # 登录状态保存（自动生成）
├── jd_login.log              # 日志文件（自动生成）
└── README.md                 # 本文件
```

## 开发计划

- [ ] 支持扫码登录
- [ ] 支持短信验证码登录
- [ ] 添加更多AI提供商支持
- [ ] 优化验证码识别准确率
- [ ] 添加Web界面
- [ ] 支持多账号管理
- [ ] 添加定时任务功能

## 许可证

本项目仅供学习研究使用，请勿用于非法用途。

## 免责声明

本工具仅用于技术研究和学习目的。使用本工具产生的任何后果由使用者自行承担。作者不对因使用本工具而导致的任何损失负责。

请遵守京东的服务条款和相关法律法规，合理使用自动化工具。

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请提交Issue。