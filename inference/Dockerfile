FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/app/artifacts/yolo26m_candidate.pt \
    PORT=8000

# Install runtime dependencies for OpenCV and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY inference/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code & candidate model
COPY inference /app/inference
COPY artifacts/yolo26m_candidate.pt /app/artifacts/yolo26m_candidate.pt

EXPOSE 8000

CMD ["sh", "-c", "exec uvicorn inference.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
