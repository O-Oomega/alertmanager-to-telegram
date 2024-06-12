# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下所有文件到工作目录
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Flask 运行的端口
EXPOSE 5001

# 使用 gunicorn 运行 Flask 应用
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "alertmanager_to_telegram:app"]
