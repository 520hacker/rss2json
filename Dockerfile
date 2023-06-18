# 第一阶段：构建阶段
FROM python:3.9 as builder

WORKDIR /build

# 安装构建所需依赖项
RUN pip install feedparser argparse requests flask

# 复制代码和配置文件到容器
COPY *.py .
COPY rss.json . 

# 第二阶段：运行阶段
FROM python:3.9-slim as runner

WORKDIR /app

# 从构建阶段复制所需的文件和依赖项 
COPY --from=builder /build/*.py .
COPY --from=builder /build/rss.json .
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# 设置环境变量
ENV ADMIN_KEY=<your_admin_key>

# 暴露端口（如果需要）
EXPOSE 5005

# 启动命令
CMD ["python", "app.py", "--admin_key", "${ADMIN_KEY}"]
