# RAG Knowledge System

A comprehensive Retrieval-Augmented Generation (RAG) knowledge management system with vector search, knowledge graph, and intelligent Q&A capabilities.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              Browser (localhost:5173)                │
│          React + TypeScript + Ant Design            │
│  ┌──────────┬──────────┬──────────┬──────────┐    │
│  │Document  │Vector    │Knowledge │Intelligent│    │
│  │Upload    │Search    │Graph     │Q&A        │    │
│  └──────────┴──────────┴──────────┴──────────┘    │
└────────────────────┬────────────────────────────────┘
                     │ HTTP REST API / SSE
┌────────────────────▼────────────────────────────────┐
│           FastAPI Backend (localhost:8000)          │
│  ┌──────────────────────────────────────────┐      │
│  │           API Routes                      │      │
│  │  /api/documents    Document CRUD          │      │
│  │  /api/vectors      Vector Search          │      │
│  │  /api/graph        Graph Query/Viz        │      │
│  │  /api/chat         RAG Q&A (SSE)          │      │
│  └──────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────┐      │
│  │          Business Logic                   │      │
│  │  - DocumentParser    Document Parsing     │      │
│  │  - VectorStore       Vector Index         │      │
│  │  - KnowledgeGraph    Graph Construction   │      │
│  │  - RAGEngine         Retrieval-Gen        │      │
│  │  - LLMClient         LLM API Calls        │      │
│  └──────────────────────────────────────────┘      │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  Data Storage                        │
│  ┌──────────┬──────────┬──────────┬──────────┐    │
│  │ChromaDB  │ SQLite   │NetworkX  │ uploads/ │    │
│  │(Vectors) │(Metadata)│(Graph)   │(Docs)    │    │
│  └──────────┴──────────┴──────────┴──────────┘    │
└─────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              External LLM API                        │
│      Zhipu AI GLM-4 / Anthropic Claude 3.5          │
└─────────────────────────────────────────────────────┘
```

## Features

- **Document Upload & Management**: Support for PDF, Word, Excel, PowerPoint, HTML, and text files
- **Vector Search**: Semantic search using sentence-transformers and ChromaDB
- **Knowledge Graph**: Graph-based knowledge representation with NetworkX
- **Intelligent Q&A**: RAG-powered question answering with streaming responses
- **Multi-LLM Support**: Integration with Zhipu AI GLM-4 and Anthropic Claude
- **Modern UI**: Responsive interface built with React and Ant Design

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Database**: SQLite (metadata), ChromaDB (vectors), NetworkX (graph)
- **Document Processing**: PyMuPDF, python-docx, openpyxl, python-pptx, BeautifulSoup4
- **Embeddings**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **RAG**: LangChain 0.1+
- **LLMs**: Zhipu AI (zhipuai), Anthropic (anthropic)

### Frontend
- **Framework**: React 18.2+
- **Language**: TypeScript 5.3+
- **Build Tool**: Vite 5.0+
- **UI Library**: Ant Design 5.12+
- **State Management**: Zustand 4.4+
- **Data Fetching**: TanStack Query 5.17+, Axios 1.6+
- **Visualization**: Recharts 2.10+
- **Markdown**: React Markdown 9.0+

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```env
ZHIPU_API_KEY=your_zhipu_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

6. Run the server:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (optional):
```bash
cp .env.example .env
```

4. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### 1. Document Upload
- Navigate to the "文档上传" (Document Upload) tab
- Drag and drop or click to upload documents
- Supported formats: PDF, DOCX, XLSX, PPTX, HTML, TXT, MD
- Documents are automatically parsed and indexed

### 2. Vector Search
- Navigate to the "向量检索" (Vector Search) tab
- Enter your search query
- Adjust the number of results (top_k) and similarity threshold
- View semantically similar document chunks

### 3. Knowledge Graph
- Navigate to the "知识图谱" (Knowledge Graph) tab
- Visualize the graph structure
- View nodes and edges in tabular format
- Check graph statistics (nodes, edges, density)

### 4. Intelligent Q&A
- Navigate to the "智能问答" (Intelligent Q&A) tab
- Toggle RAG mode on/off
- Adjust retrieval parameters
- Chat with streaming responses
- View retrieved documents in real-time

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Key Endpoints

#### Documents
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents/` - List all documents
- `GET /api/documents/{id}` - Get document by ID
- `DELETE /api/documents/{id}` - Delete document

#### Vectors
- `POST /api/vectors/search` - Search similar chunks
- `GET /api/vectors/stats` - Get statistics

#### Graph
- `GET /api/graph/` - Get knowledge graph
- `POST /api/graph/nodes` - Create node
- `POST /api/graph/edges` - Create edge
- `GET /api/graph/stats` - Get statistics

#### Chat
- `POST /api/chat/stream` - Streaming chat with RAG (SSE)
- `POST /api/chat/message` - Non-streaming chat
- `GET /api/chat/models` - Get available models

## Configuration

### Backend Configuration (`backend/.env`)

Key configuration options:

- `CHUNK_SIZE`: Text chunk size for splitting (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `RETRIEVAL_TOP_K`: Number of chunks to retrieve (default: 5)
- `SIMILARITY_THRESHOLD`: Minimum similarity score (default: 0.7)
- `LLM_TEMPERATURE`: LLM temperature (default: 0.7)
- `LLM_MAX_TOKENS`: Maximum tokens to generate (default: 2000)

### Frontend Configuration (`frontend/.env`)

- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python main.py
```

The server will auto-reload on code changes when `DEBUG=true`.

### Frontend Development

```bash
cd frontend
npm run dev
```

Vite provides hot module replacement for instant updates.

### Building for Production

#### Backend
No build step required. Deploy with a production ASGI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend
```bash
cd frontend
npm run build
npm run preview  # Preview production build
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── documents.py
│   │   │       ├── vectors.py
│   │   │       ├── graph.py
│   │   │       └── chat.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   └── document.py
│   │   ├── schemas/
│   │   │   └── document.py
│   │   └── services/
│   │       ├── document_parser.py
│   │       ├── vector_store.py
│   │       ├── knowledge_graph.py
│   │       ├── llm_client.py
│   │       └── rag_engine.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── VectorSearch.tsx
│   │   │   ├── KnowledgeGraph.tsx
│   │   │   └── Chat.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── documentService.ts
│   │   │   ├── vectorService.ts
│   │   │   ├── graphService.ts
│   │   │   └── chatService.ts
│   │   ├── store/
│   │   │   └── index.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── styles/
│   │   │   ├── index.css
│   │   │   └── App.css
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
└── README.md
```

## Troubleshooting

### Backend Issues

**ChromaDB errors**:
- Ensure `CHROMA_PERSIST_DIR` directory is writable
- Delete and recreate if corrupted

**LLM API errors**:
- Verify API keys in `.env`
- Check network connectivity
- Review API quotas and limits

**Document parsing errors**:
- Ensure all dependencies are installed
- Check file permissions
- Verify file format is supported

### Frontend Issues

**API connection errors**:
- Verify backend is running on port 8000
- Check CORS settings in backend
- Ensure `VITE_API_BASE_URL` is correct

**Build errors**:
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf .vite`

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.