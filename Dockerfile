# 使用 Python 3.10 slim 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件（排除 .env）
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# 设置默认启动命令
CMD ["python", "funclip/launch.py", "--listen"]