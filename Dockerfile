# 生产镜像:仅安装运行依赖(开发/检查依赖只在 CI 安装,见规范 05)
FROM python:3.11-slim

WORKDIR /app

# 镜像源可配置:国内服务器构建时传 --build-arg PIP_INDEX_URL=<国内源>
ARG PIP_INDEX_URL=https://pypi.org/simple
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

COPY app/ ./app/
COPY models/ ./models/
COPY data/ ./data/
COPY run.py ./run.py

EXPOSE 8888

# Streamlit 内置健康端点 /_stcore/health(无 curl 的 slim 镜像用 python 探测)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8888/_stcore/health', timeout=3)"

# run.py 会把仓库根目录加入 sys.path,保证 import app 可用
CMD ["streamlit", "run", "run.py", "--server.port=8888", "--server.address=0.0.0.0", "--server.headless=true"]
