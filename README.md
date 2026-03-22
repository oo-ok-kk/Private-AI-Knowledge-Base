Private-AI-Knowledge-Base 🤖
一个基于 DeepSeek 与 LlamaIndex 构建的轻量化、隐私优先的私有 AI 知识库系统。该项目实现了从本地 PDF 数字化到向量检索，再到 Web 端交互的完整 AI 工作流，并支持 Docker 一键跨平台部署。

🌟 项目亮点
高精度 PDF 解析：集成 PyMuPDFReader 引擎，针对复杂排版的简历、技术文档进行精准文字提取，告别传统解析的乱码问题。

低成本高性能：采用 DeepSeek-V3 模型作为推理核心，配合本地 BGE 向量模型，兼顾响应速度与运行成本。

容器化生产架构：通过 Docker 环境隔离，支持 macOS (Server) 与 Windows (Client) 的跨设备协同办公。

安全性设计：全链路环境变量解耦，数据库与敏感信息本地化存储，杜绝 API Key 泄露风险。

🧠 RAG 核心工作流 (RAG Workflow)
本项目实现了一个标准的生产级 RAG 架构，将非结构化的 PDF 文档转化为可检索的知识库：

1. 数据入库阶段 (Data Ingestion Pipeline)
精准解析：利用 PyMuPDFReader 引擎对原始 PDF 进行流式读取，确保段落格式与特殊字符的完整性。

语义切片：通过 LlamaIndex 的 NodeParser 将长文本切分为具有语义联系的文本块（Nodes）。

向量化存储：调用本地 BGE-small-zh 嵌入模型，将文本转化为 512 维稠密向量，持久化存储于 ChromaDB。

2. 检索与生成阶段 (Retrieval & Generation)
语义检索 (Retrieval)：当用户提问时，系统实时计算查询词的向量，在 ChromaDB 中进行相似度搜索（Top-K）。

上下文增强 (Augmentation)：将检索到的最相关知识片段封装进系统提示词（System Prompt）。

智能生成 (Generation)：通过 DeepSeek-V3 模型在限定的上下文范围内进行逻辑推理，确保回答的真实性与针对性。

🏗️ 系统架构
数据层 (Ingestion)：使用 PyMuPDF 读取 PDF，通过 BGE-small-zh 模型向量化并持久化至 ChromaDB。

服务层 (Backend)：基于 FastAPI 构建异步接口，管理 LlamaIndex 查询引擎。

应用层 (Frontend)：使用 Streamlit 构建响应式 Web 界面，支持实时对话与文档管理。

部署层 (DevOps)：利用 Docker 实现前后端多进程协同调度。

🛠️ 技术栈
LLM: DeepSeek-V3 (via API)

Framework: LlamaIndex, FastAPI

Vector DB: ChromaDB

Embedding: BAAI/bge-small-zh-v1.5

Frontend: Streamlit

Deployment: Docker, OrbStack

🚀 快速开始
1. 克隆仓库
Bash
git clone https://github.com/your-username/Private-AI-Knowledge-Base.git
cd Private-AI-Knowledge-Base
2. 配置环境
复制模板文件并填入你的 DEEPSEEK_API_KEY:

Bash
cp .env.example .env
3. Docker 一键启动
Bash
# 构建镜像
docker build -t ai-assistant .

# 启动容器（自动挂载本地数据与索引）
docker run -d \
  -p 8000:8000 -p 8501:8501 \
  --name my-ai-bot \
  -e DEEPSEEK_API_KEY="你的KEY" \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/chroma_db:/app/chroma_db" \
  ai-assistant
📂 目录结构说明
ingest.py: 数据预处理与向量化脚本。

server.py: FastAPI 后端核心逻辑。

web_app.py: Streamlit 交互界面。

query.py: 命令行快速调试工具。

start.command: Docker 容器内部启动调度脚本。

data/: 存放待解析的 PDF 文档（已忽略）。

chroma_db/: 持久化向量数据库（已忽略）。

💡 开发思考
在构建此项目的过程中，重点解决了以下工程化挑战：

环境一致性：通过 Docker 解决了 Mac mini (M1/M4) 架构与 Windows 客户端之间的访问隔离问题。

RAG 准确度提升：对比了多种 PDF 解析器，最终选定 PyMuPDF 以支持更细粒度的段落提取，显著提升了检索的准确性。

解耦设计：实现了推理模型（LLM）与向量存储（Vector Store）的插件化配置，支持分钟级切换至 OpenAI 或 Pinecone。
