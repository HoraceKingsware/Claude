# Knowledge Base RAG 应用

一个功能完整的知识库管理和RAG（检索增强生成）问答系统，支持文档解析、向量检索、知识图谱和智能问答。

## 📋 项目概述

本项目是一个基于RAG技术的知识库管理系统，可以帮助用户：
- 管理多个知识库
- 上传和解析各种格式的文档
- 通过向量检索快速查找相关信息
- 使用LLM进行智能问答
- 可视化知识图谱

## ✨ 核心功能

### 1. 知识库管理
- ✅ 创建、查看、编辑和删除知识库
- ✅ 支持多知识库隔离管理
- ✅ 知识库统计信息展示

### 2. 文档处理
- ✅ 支持多种文档格式：
  - PDF (.pdf)
  - Word (.docx, .doc)
  - PowerPoint (.pptx, .ppt)
  - 文本文件 (.txt)
  - Markdown (.md, .markdown)
  - HTML (.html, .htm)
- ✅ 自动文档解析和分块
- ✅ 文档上传进度和状态追踪
- ✅ 文档管理（查看、删除）

### 3. 向量检索
- ✅ 基于语义的向量检索
- ✅ ChromaDB 持久化存储
- ✅ 可配置的相似度阈值
- ✅ 多文档来源追溯

### 4. 智能问答（RAG）
- ✅ 基于知识库的问答
- ✅ 上下文感知的对话
- ✅ 流式响应（实时打字效果）
- ✅ 答案来源引用
- ✅ 对话历史记录
- ✅ 支持 OpenAI 和 Anthropic Claude

### 5. 知识图谱
- ✅ 自动实体识别
- ✅ 关系抽取
- ✅ 图谱可视化
- ✅ 交互式图谱探索

## 🛠 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **向量数据库**: ChromaDB 0.4+
- **LLM集成**:
  - OpenAI GPT-4
  - Anthropic Claude 3
- **RAG框架**: LangChain
- **文档处理**:
  - PyPDF2 (PDF)
  - python-docx (Word)
  - python-pptx (PowerPoint)
- **知识图谱**: NetworkX
- **数据库**: SQLite (可扩展到 PostgreSQL)
- **嵌入模型**: Sentence Transformers

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite 5
- **UI库**: Ant Design 5
- **路由**: React Router 6
- **图谱可视化**: ReactFlow
- **HTTP客户端**: Axios

## 📦 项目结构

```
.
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   └── endpoints/  # API端点
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   │   ├── document_parser.py    # 文档解析
│   │   │   ├── vector_store.py       # 向量存储
│   │   │   ├── knowledge_graph.py    # 知识图谱
│   │   │   └── llm_service.py        # LLM服务
│   │   └── main.py         # 主应用
│   ├── requirements.txt    # Python依赖
│   └── .env.example        # 环境变量示例
│
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   ├── types/          # TypeScript类型
│   │   └── App.tsx         # 主应用组件
│   ├── package.json        # Node依赖
│   └── vite.config.ts      # Vite配置
│
└── README.md               # 项目文档
```

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 18+
- npm 或 yarn

### 1. 后端安装

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（Windows）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入 API Keys
```

**重要**: 在 `.env` 文件中配置以下内容：

```env
# OpenAI (可选，二选一)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude (可选，二选一)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 选择默认LLM提供商
DEFAULT_LLM_PROVIDER=openai  # 或 anthropic
```

### 2. 前端安装

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 3. 运行项目

#### 启动后端

```bash
cd backend
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 `http://localhost:8000` 运行

#### 启动前端

```bash
cd frontend
npm run dev
```

前端将在 `http://localhost:5173` 运行

### 4. 访问应用

打开浏览器访问: `http://localhost:5173`

## 📖 使用指南

### 1. 创建知识库

1. 点击"新建知识库"按钮
2. 输入知识库名称和描述
3. 点击确认创建

### 2. 上传文档

1. 选择一个知识库
2. 点击"上传文档"按钮
3. 选择文件（支持 PDF、Word、PowerPoint、TXT、Markdown、HTML）
4. 等待文档处理完成

### 3. 开始对话

1. 点击知识库的"对话"按钮
2. 在输入框中输入问题
3. 系统会基于知识库内容回答问题
4. 可以查看答案的来源文档

### 4. 查看知识图谱

1. 点击知识库的"知识图谱"按钮
2. 查看自动生成的实体和关系图谱
3. 可以拖拽和缩放图谱
4. 点击"重建图谱"更新内容

## 🔧 配置说明

### 后端配置 (.env)

```env
# API配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS设置
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# 数据库
DATABASE_URL=sqlite:///./knowledge_base.db

# 向量数据库
CHROMA_PERSIST_DIRECTORY=./chroma_db

# LLM配置
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
DEFAULT_LLM_PROVIDER=openai

# 嵌入模型
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# 文件上传
MAX_UPLOAD_SIZE=52428800  # 50MB
UPLOAD_DIR=./uploads

# 知识图谱
ENABLE_KNOWLEDGE_GRAPH=true

# 日志
LOG_LEVEL=INFO
```

### 前端配置 (vite.config.ts)

前端代理已配置，会自动将 `/api` 请求转发到后端 `http://localhost:8000`

## 🧪 API 文档

启动后端后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 核心 API 端点

### 知识库管理
- `POST /api/knowledge-bases/` - 创建知识库
- `GET /api/knowledge-bases/` - 获取知识库列表
- `GET /api/knowledge-bases/{kb_id}` - 获取知识库详情
- `PUT /api/knowledge-bases/{kb_id}` - 更新知识库
- `DELETE /api/knowledge-bases/{kb_id}` - 删除知识库

### 文档管理
- `POST /api/knowledge-bases/{kb_id}/upload` - 上传文档
- `GET /api/knowledge-bases/{kb_id}/documents` - 获取文档列表
- `DELETE /api/knowledge-bases/{kb_id}/documents/{doc_id}` - 删除文档

### 问答
- `POST /api/query/` - 普通问答
- `POST /api/query/stream` - 流式问答

### 对话
- `GET /api/knowledge-bases/{kb_id}/conversations` - 获取对话列表
- `GET /api/knowledge-bases/conversations/{conv_id}` - 获取对话详情

### 知识图谱
- `GET /api/knowledge-bases/{kb_id}/graph` - 获取知识图谱
- `POST /api/knowledge-bases/{kb_id}/graph/rebuild` - 重建知识图谱

## 🎯 功能特性详解

### RAG 检索增强生成

系统使用以下流程实现RAG：

1. **文档处理**: 上传的文档被解析并分块（默认1000字符，重叠200字符）
2. **向量化**: 使用 Sentence Transformers 生成嵌入向量
3. **存储**: 向量存储在 ChromaDB 中
4. **检索**: 用户提问时，系统检索最相关的文档块（默认top-5）
5. **生成**: 将检索结果作为上下文，使用LLM生成答案

### 知识图谱构建

系统自动从文档中提取：

- **实体**: 使用规则和模式识别命名实体
- **关系**: 识别常见关系模式（is_a、has、uses等）
- **可视化**: 使用ReactFlow展示实体关系图

## 🔐 安全建议

1. **API密钥**: 不要在代码中硬编码API密钥，使用环境变量
2. **文件上传**: 系统已限制文件大小和类型
3. **CORS**: 生产环境需要配置正确的 ALLOWED_ORIGINS
4. **数据库**: 生产环境建议使用 PostgreSQL 替代 SQLite

## 🚧 待优化功能

- [ ] 用户认证和权限管理
- [ ] 更高级的知识图谱算法（使用 spaCy NER）
- [ ] 支持更多LLM提供商
- [ ] 文档预览功能
- [ ] 批量文档上传
- [ ] 导出对话记录
- [ ] 多语言支持
- [ ] Docker容器化部署

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 GitHub Issue。

---

**详细部署指南**: 请查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解 Windows 11 环境下的详细部署步骤。

**注意**: 本项目仅供学习和研究使用。在生产环境中使用前，请确保进行充分的测试和安全加固。