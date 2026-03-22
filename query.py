import os
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.deepseek import DeepSeek
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. 配置安全的环境变量读取 ---
# 从系统环境读取，彻底告别硬编码
api_key = os.environ.get("DEEPSEEK_API_KEY")

if not api_key:
    print("❌ 错误：未在环境变量中找到 DEEPSEEK_API_KEY")
    print("💡 提示：运行容器时请加上 -e DEEPSEEK_API_KEY='你的KEY'")
    exit(1)

Settings.llm = DeepSeek(
    model="deepseek-chat", 
    api_key=api_key
)

# 使用本地 BGE 模型进行查询向量化
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

def run_query():
    # --- 2. 检查并连接数据库 ---
    db_path = "./chroma_db"
    
    # 在查询前先确认数据库是否存在，否则检索会报错
    if not os.path.exists(db_path):
        print(f"❌ 错误：找不到向量数据库路径 {db_path}。")
        print("💡 提示：请先运行 ingest.py 来扫描 PDF 文件并生成索引。")
        return

    db = chromadb.PersistentClient(path=db_path)
    chroma_collection = db.get_or_create_collection("my_private_data")
    
    # --- 3. 重建索引映射 ---
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # 直接加载现有的向量库
    # 这里通过 vector_store 映射，不需要重新读取 data 文件夹
    index = VectorStoreIndex.from_vector_store(vector_store)
    
    # --- 4. 开启查询对话 ---
    # streaming=True 开启流式响应，像打字机一样逐字显示
    query_engine = index.as_query_engine(streaming=True)
    
    print("\n" + "="*40)
    print("🤖 你的私有 AI 知识库已上线！")
    print("提示：输入 'exit' 或 '退出' 即可结束对话")
    print("="*40)

    while True:
        try:
            user_input = input("\n🤔 请输入你的问题: ")
            
            if user_input.strip().lower() in ['exit', 'quit', '退出']:
                print("再见！祝你工作流开发顺利！")
                break
            
            if not user_input.strip():
                continue

            print("\n>>> 正在检索并思考中...")
            response = query_engine.query(user_input)
            
            print(">>> AI 回答:")
            response.print_response_stream()
            print("\n" + "-"*40)
            
        except KeyboardInterrupt:
            # 优雅处理 Ctrl+C 退出
            print("\n👋 强制退出，下次再见！")
            break

if __name__ == "__main__":
    run_query()