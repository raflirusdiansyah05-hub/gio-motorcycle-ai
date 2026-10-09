FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8501 \
    INFERENCE_API_URL=http://127.0.0.1:8000

# Install runtime utilities (curl untuk healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install frontend dependencies (tanpa PyTorch/Ultralytics)
COPY dashboard/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code dashboard dan konfigurasi Streamlit
COPY dashboard /app/dashboard
COPY .streamlit /app/.streamlit

EXPOSE 8501

CMD ["sh", "-c", "exec streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port ${PORT:-8501} --server.headless true"]
