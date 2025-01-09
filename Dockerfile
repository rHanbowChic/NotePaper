# 使用官方 Python 作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制应用代码到容器中
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置 Flask 运行时环境变量
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 暴露端口
EXPOSE 5000

# 启动 Flask 应用
CMD ["flask", "run"]