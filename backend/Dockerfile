# Multi-stage Dockerfile for PocketSmart AI FastAPI Backend
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final runtime stage
FROM python:3.12-slim

WORKDIR /app

# Security: Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy virtual environment from builder to /opt/venv
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application source code
COPY app/ /app/app/

# Set ownership
RUN chown -R appuser:appuser /app /opt/venv

# Switch to non-root user
USER appuser

# Expose default backend port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + str(__import__('os').environ.get('PORT', '8000')) + '/api/v1/health')" || exit 1

# Launch production ASGI server supporting both local ($PORT unset -> 8000) and Render ($PORT set -> e.g. 10000)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
