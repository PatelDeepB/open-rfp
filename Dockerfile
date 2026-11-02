FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OPENRFP_HOST=0.0.0.0 \
    OPENRFP_PORT=8000 \
    OPENRFP_DATA_DIR=/app/data/storage

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY openrfp ./openrfp
COPY data/samples ./data/samples

RUN pip install --no-cache-dir .

RUN mkdir -p /app/data/storage

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["open-rfp", "serve", "--host", "0.0.0.0", "--port", "8000"]
