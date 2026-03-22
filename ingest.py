import os
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.deepseek import DeepSeek
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PyMuPDFReader

# --- 1. 配置安全的环境变量读取 ---
api_key = os.environ.get("DEEPSEEK_API_KEY")

if not api_key:
    # 如果没找到 Key，给出专业且友好的提示
    print("❌ 错误：环境变量中未找到 DEEPSEEK_API_KEY。")
    print("💡 提示：请确保在 .env 文件中配置了它，或在 Docker 启动命令中使用 -e 注入。")
    exit(1)

Settings.llm = DeepSeek(
    model="deepseek-chat", 
    api_key=api_key 
)

# 嵌入模型配置保持不变
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

def start_ingest():
    # --- 2. 初始化持久化数据库 ---
    # 路径使用相对路径，方便 Docker 挂载
    db = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = db.get_or_create_collection("my_private_data")
    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # --- 3. 使用 PyMuPDF 引擎精准读取 ---
    data_path = "./data"
    
    # 检查 data 目录是否存在，防止 Docker 挂载失败报错
    if not os.path.exists(data_path):
        print(f"❌ 错误：找不到目录 {data_path}，请检查路径。")
        return

    print(f">>> 正在通过 PyMuPDF 引擎精准读取 {data_path} ...")
    
    loader = SimpleDirectoryReader(
        input_dir=data_path,
        file_extractor={".pdf": PyMuPDFReader()}
    )
    documents = loader.load_data()
    
    if not documents:
        print("❌ 错误：没读到东西，请检查 data 文件夹里是否有 PDF。")
        return

    # --- 4. 解析自检预览 ---
    print("\n" + "="*40)
    print("🔍 [解析自检] AI 读到的前 100 个字：")
    preview_text = documents[0].text[:100].replace('\n', ' ')
    print(f"{preview_text}...")
    print("="*40 + "\n")

    # --- 5. 向量化并入库 ---
    print(f"🚀 正在将 {len(documents)} 个片段存入向量数据库...")
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context, 
        show_progress=True
    )
    
    print("✅ 任务完成！现在数据库里的知识是精准的文字了。")

if __name__ == "__main__":
    start_ingest()