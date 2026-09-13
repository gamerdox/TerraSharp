# Multistage Dockerfile for SH-304
FROM python:3.11-slim as backend

WORKDIR /app

# Install system GDAL / GEOS libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY configs/ ./configs/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Generate seed demo data
RUN python scripts/seed_demo_data.py

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
