#!/bin/bash

# 美团自动登录 - 快速启动脚本

echo "==================================="
echo "   美团自动登录系统"
echo "==================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "检测到未创建虚拟环境，正在创建..."
    python3 -m venv venv
    echo "✓ 虚拟环境已创建"
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source venv/bin/activate

# 检查依赖
if [ ! -f "venv/installed" ]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt

    echo "正在安装Playwright浏览器..."
    playwright install chromium

    # 标记已安装
    touch venv/installed
    echo "✓ 依赖安装完成"
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo ""
    echo "警告: 未找到.env文件，请先配置环境变量"
    echo "运行命令: cp .env.example .env"
    echo "然后编辑.env文件，填入账号密码和API密钥"
    echo ""
    read -p "是否现在创建.env文件? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✓ .env文件已创建，请编辑后重新运行"
        exit 0
    fi
fi

# 运行程序
echo ""
echo "正在启动美团自动登录..."
echo ""
python -m meituan_auto_login.main

# 退出虚拟环境
deactivate
