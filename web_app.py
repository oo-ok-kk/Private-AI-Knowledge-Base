import streamlit as st
import requests
import os

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="Private AI Knowledge Base", page_icon="🤖", layout="wide")

# 获取后端地址：优先从环境变量读取，默认为本地容器内地址
# 这样在 Docker 内部运行时，它们可以通过 localhost 互相通信
API_BASE = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

# --- 2. 侧边栏：知识管理 ---
with st.sidebar:
    st.title("⚙️ 知识工厂")
    st.markdown("---")
    
    # 文件上传组件
    uploaded_file = st.file_uploader("上传新的 PDF 文档", type="pdf")
    if uploaded_file is not None:
        if st.button("🚀 让 AI 学习该文件"):
            # 这里的逻辑建议：在开源版中，由于 ingest 脚本通常是独立运行的，
            # 这里的上传功能可以提示用户将文件放入 /data 目录，或者对接专门的 /upload 接口
            with st.spinner("正在解析文档并构建索引..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    # 注意：如果你的 server.py 还没有写 /upload 接口，这里会报错
                    res = requests.post(f"{API_BASE}/upload", files=files, timeout=60)
                    if res.status_code == 200:
                        st.success("✅ 知识库同步成功！")
                    else:
                        st.error(f"上传失败，状态码：{res.status_code}")
                except Exception as e:
                    st.error(f"连接后端失败: {str(e)}")
    
    st.markdown("---")
    if st.button("🗑️ 清空当前对话记录"):
        st.session_state.messages = []
        st.rerun()

# --- 3. 主界面：聊天窗口 ---
st.title("💬 私有知识库对话系统")

# 初始化消息队列
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. 用户输入提问 ---
if prompt := st.chat_input("针对文档内容或通用知识进行提问..."):
    # 展示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 请求助手回答
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # 对齐 server.py 的接口：POST 请求 /chat，数据格式 {"message": "..."}
                payload = {"message": prompt}
                res = requests.post(f"{API_BASE}/chat", json=payload, timeout=30)
                
                if res.status_code == 200:
                    # 对齐 server.py 的返回格式：{"response": "..."}
                    answer = res.json().get("response", "未能解析到有效回答")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"后端响应异常 (状态码: {res.status_code})")
            except Exception as e:
                st.error(f"❌ 无法连接到后台服务器，请检查后端容器是否正常运行。")