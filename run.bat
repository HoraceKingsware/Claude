@echo off
chcp 65001 >nul
:: 美团自动登录 - Windows快速启动脚本

echo ===================================
echo    美团自动登录系统
echo ===================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist "venv" (
    echo 检测到未创建虚拟环境，正在创建...
    python -m venv venv
    echo ✓ 虚拟环境已创建
)

:: 激活虚拟环境
echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

:: 检查依赖
if not exist "venv\installed" (
    echo 正在安装依赖...
    pip install -r requirements.txt

    echo 正在安装Playwright浏览器...
    playwright install chromium

    :: 标记已安装
    type nul > venv\installed
    echo ✓ 依赖安装完成
)

:: 检查配置文件
if not exist ".env" (
    echo.
    echo 警告: 未找到.env文件，请先配置环境变量
    echo 运行命令: copy .env.example .env
    echo 然后编辑.env文件，填入账号密码和API密钥
    echo.
    set /p REPLY="是否现在创建.env文件? (y/n) "
    if /i "%REPLY%"=="y" (
        copy .env.example .env
        echo ✓ .env文件已创建，请编辑后重新运行
        pause
        exit /b 0
    )
)

:: 运行程序
echo.
echo 正在启动美团自动登录...
echo.
python -m meituan_auto_login.main

:: 退出虚拟环境
call venv\Scripts\deactivate.bat

pause
