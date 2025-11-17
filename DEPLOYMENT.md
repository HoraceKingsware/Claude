# 部署指南 - Windows 11

本文档详细说明如何在 Windows 11 个人电脑上部署 Knowledge Base RAG 应用。

## 🖥 系统要求

- Windows 11
- Python 3.9 或更高版本
- Node.js 18 或更高版本
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

## 📋 安装步骤

### 1. 安装 Python

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.9+ for Windows
3. 运行安装程序
   - ✅ 勾选 "Add Python to PATH"
   - ✅ 勾选 "Install pip"
4. 验证安装:
   ```cmd
   python --version
   pip --version
   ```

### 2. 安装 Node.js

1. 访问 [Node.js 官网](https://nodejs.org/)
2. 下载 LTS 版本（推荐 18.x 或 20.x）
3. 运行安装程序（使用默认设置）
4. 验证安装:
   ```cmd
   node --version
   npm --version
   ```

### 3. 克隆或下载项目

```cmd
# 如果使用 Git
git clone <repository-url>
cd Claude

# 或者直接下载 ZIP 文件并解压
```

## 🔧 后端部署

### 1. 创建 Python 虚拟环境

```cmd
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 你应该看到命令提示符前面出现 (venv)
```

### 2. 安装 Python 依赖

```cmd
# 升级 pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 这可能需要几分钟时间
```

**可能遇到的问题**:

如果安装失败，尝试：

```cmd
# 使用国内镜像源（更快）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者单独安装失败的包
pip install <package-name> --upgrade
```

### 3. 配置环境变量

```cmd
# 复制环境变量模板
copy .env.example .env

# 使用记事本编辑 .env 文件
notepad .env
```

**必须配置的内容**:

```env
# 至少配置一个 LLM API Key

# 选项1: 使用 OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_LLM_PROVIDER=openai

# 选项2: 使用 Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
DEFAULT_LLM_PROVIDER=anthropic
```

**获取 API Key**:

- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

### 4. 初始化数据库

后端首次启动时会自动创建数据库，无需手动操作。

### 5. 启动后端服务

```cmd
# 确保在 backend 目录且虚拟环境已激活
python -m app.main
```

你应该看到:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**后端现在运行在**: `http://localhost:8000`

测试后端:
- 浏览器访问: `http://localhost:8000`
- API 文档: `http://localhost:8000/docs`

## 🎨 前端部署

### 1. 安装 Node 依赖

打开**新的命令提示符窗口**（保持后端运行）:

```cmd
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 这可能需要几分钟时间
```

**可能遇到的问题**:

如果安装慢或失败:

```cmd
# 使用国内镜像源
npm config set registry https://registry.npmmirror.com
npm install

# 或使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

### 2. 启动前端开发服务器

```cmd
# 确保在 frontend 目录
npm run dev
```

你应该看到:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**前端现在运行在**: `http://localhost:5173`

## 🌐 访问应用

1. 打开浏览器（推荐 Chrome 或 Edge）
2. 访问: `http://localhost:5173`
3. 你应该看到知识库管理界面

## 📝 日常使用

### 启动应用

每次使用需要启动两个服务：

**终端 1 - 后端**:
```cmd
cd backend
venv\Scripts\activate
python -m app.main
```

**终端 2 - 前端**:
```cmd
cd frontend
npm run dev
```

### 停止应用

在两个终端窗口中按 `Ctrl+C` 停止服务。

## 🔍 故障排查

### 后端问题

**问题**: 端口 8000 已被占用
```cmd
# 查找占用端口的进程
netstat -ano | findstr :8000

# 终止该进程（使用上面命令显示的 PID）
taskkill /PID <PID> /F

# 或修改 .env 中的端口
API_PORT=8001
```

**问题**: 导入模块失败
```cmd
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

**问题**: ChromaDB 错误
```cmd
# 删除数据库重新初始化
rmdir /s chroma_db
# 重启后端
```

### 前端问题

**问题**: 端口 5173 已被占用
```cmd
# 终止占用的进程
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**问题**: API 请求失败
1. 检查后端是否运行在 8000 端口
2. 检查浏览器控制台错误
3. 验证 vite.config.ts 中的代理配置

**问题**: 依赖安装失败
```cmd
# 清理缓存
npm cache clean --force

# 删除 node_modules 重新安装
rmdir /s node_modules
del package-lock.json
npm install
```

## 📊 性能优化

### 后端优化

1. **使用更快的嵌入模型**:
   ```env
   # .env
   EMBEDDING_MODEL=sentence-transformers/paraphrase-MiniLM-L3-v2
   ```

2. **调整分块大小**:
   编辑 `backend/app/services/document_parser.py`:
   ```python
   text_chunker = TextChunker(chunk_size=500, chunk_overlap=100)
   ```

3. **使用更快的数据库**:
   - 安装 PostgreSQL
   - 修改 DATABASE_URL

### 前端优化

1. **生产构建**:
   ```cmd
   npm run build
   # 产物在 dist/ 目录
   ```

2. **使用 http-server 提供静态文件**:
   ```cmd
   npm install -g http-server
   cd dist
   http-server -p 5173
   ```

## 🐳 Docker 部署（可选）

如果你安装了 Docker Desktop for Windows:

```cmd
# 构建镜像
docker-compose build

# 启动服务
docker-compose up
```

## 🔒 安全建议

### 开发环境
- ✅ 使用 .env 文件管理密钥
- ✅ 不要提交 .env 到版本控制
- ✅ 定期更新依赖包

### 生产环境
- 🔐 使用 HTTPS
- 🔐 设置强密码和访问控制
- 🔐 配置防火墙规则
- 🔐 定期备份数据库

## 📂 数据位置

应用运行后会在以下位置存储数据：

```
backend/
├── knowledge_base.db      # SQLite 数据库
├── chroma_db/            # 向量数据库
└── uploads/              # 上传的文件
    └── kb_<id>/         # 每个知识库的文件夹
```

**备份**: 定期备份这些目录！

## 🔄 更新应用

```cmd
# 更新代码
git pull

# 更新后端依赖
cd backend
venv\Scripts\activate
pip install -r requirements.txt --upgrade

# 更新前端依赖
cd frontend
npm install
```

## 📞 获取帮助

遇到问题？

1. 查看日志输出
2. 检查 API 文档: `http://localhost:8000/docs`
3. 查看浏览器控制台（F12）
4. 提交 GitHub Issue

## 🎉 成功部署检查清单

- [ ] Python 3.9+ 已安装
- [ ] Node.js 18+ 已安装
- [ ] 后端依赖已安装
- [ ] 前端依赖已安装
- [ ] .env 文件已配置（包含 API Key）
- [ ] 后端运行在 8000 端口
- [ ] 前端运行在 5173 端口
- [ ] 可以访问 http://localhost:5173
- [ ] 可以创建知识库
- [ ] 可以上传文档
- [ ] 可以进行对话

全部完成？恭喜你成功部署了 Knowledge Base RAG 应用！🎊
