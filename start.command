#!/bin/bash

# ==========================================
# Private AI Knowledge Base - Startup Script
# ==========================================

echo "🚀 Starting Private AI Workflow (Docker Mode)..."

# 1. 启动后端大脑 (FastAPI)
# 移除了日志屏蔽，以便通过 docker logs 监控后端状态
echo "🧠 Waking up Backend (FastAPI)..."
python server.py &

# 记录大脑的进程 ID，方便同步关闭
SERVER_PID=$!

# 2. 稍等 3 秒，确保后端完全启动
sleep 3

# 3. 启动前端网页 (Streamlit)
# --server.address 0.0.0.0 是确保局域网（如你的 ROG 幻16）可访问的关键
echo "🎨 Loading Frontend Interface (Streamlit)..."
streamlit run web_app.py --server.port 8501 --server.address 0.0.0.0

# 4. 当容器停止时，自动清理后台进程
kill $SERVER_PID
echo "👋 All services stopped. See you next time!"