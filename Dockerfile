# ==========================================
# Multi-stage Dockerfile for DocxMath Studio
# ==========================================

# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Backend & Runtime
FROM python:3.11-slim

# Install system dependencies including Pandoc
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy built frontend assets from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy test data and environment
COPY test_data/ ./test_data/
COPY .env.example ./.env

ENV PYTHONPATH=/app/backend
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
