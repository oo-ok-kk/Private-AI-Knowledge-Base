import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.deepseek import DeepSeek
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

app = FastAPI(title="Private Knowledge Base AI Backend")

# --- 1. 安全配置：从环境读取 API Key ---
api_key = os.environ.get("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("❌ Start failed: DEEPSEEK_API_KEY environment variable not detected!")

Settings.llm = DeepSeek(model="deepseek-chat", api_key=api_key)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

# --- 2. 数据库连接 ---
db_path = "./chroma_db"
db = chromadb.PersistentClient(path=db_path)
chroma_collection = db.get_or_create_collection("my_private_data")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
index = VectorStoreIndex.from_vector_store(vector_store)
query_engine = index.as_query_engine()

# --- 3. 定义数据格式 ---
class ChatRequest(BaseModel):
    message: str

# --- 4. 核心对话接口 ---
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
            
        response = query_engine.query(request.message)
        return {"response": str(response)}
    except Exception as e:
        print(f"🔥 后端报错: {str(e)}")
        raise HTTPException(status_code=500, detail="AI backend disconnected")

# --- 5. 启动配置 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)