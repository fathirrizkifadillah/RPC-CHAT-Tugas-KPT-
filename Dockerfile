# syntax=docker/dockerfile:1
# Multi-stage / optimized Dockerfile for Distributed Chat Room RPC

FROM python:3.11-slim AS base

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Install dependencies layer
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy source code and proto definitions
COPY proto/ ./proto/
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY pyproject.toml .

# Generate stubs inside container to ensure platform compatibility
RUN python scripts/generate_stubs.py

# Security: Non-root user setup
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 50051

# Default command runs the gRPC server
CMD ["python", "src/chat_room/server.py", "--host", "0.0.0.0", "--port", "50051"]
