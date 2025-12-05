# ============================================================
# ✅ OPTIMIZED: Proper layer ordering for fast rebuilds
# Code changes rebuild in seconds, not minutes!
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# ============================================================
# LAYER 1: Dependencies (changes rarely)
# This layer is CACHED until requirements.txt changes
# ============================================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# LAYER 2: Application code (changes frequently)  
# Only THIS layer rebuilds when you change code!
# ============================================================
COPY app.py .

# ============================================================
# Production settings
# ============================================================
ENV OLLAMA_HOST=http://host.docker.internal:11434
ENV DEFAULT_MODEL=llama3.2

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "app:app"]
