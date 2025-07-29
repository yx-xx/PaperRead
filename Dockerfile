FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的数据目录
RUN mkdir -p Data/PC_Data/downloads \
    Data/PC_Data/logs \
    Data/PC_Data/output \
    Data/PR_Data/glm_outputs \
    Data/PR_Data/prompt_outputs \
    Data/PR_Data/qwen_outputs \
    Data/PR_Data/paper

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 设置默认命令
CMD ["bash"]
