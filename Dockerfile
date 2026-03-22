# 1. 使用官方轻量级 Python 环境
FROM python:3.11-slim

# 2. 设置容器内的工作目录
WORKDIR /app

# 3. 先把清单考进去
COPY requirements.txt .

# 4. 先升级 pip (使用清华源，这是为了让它能更快解析复杂的依赖关系)
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 安装依赖 (使用清华源)
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 6. 把当前目录下的其他代码拷进去 (这行一定要放在 pip 安装之后，这样改代码就不需要重新装包)
COPY . .

# 7. 端口与启动
EXPOSE 8000
EXPOSE 8501
RUN chmod +x start.command
CMD ["./start.command"]