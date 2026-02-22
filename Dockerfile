# TeXForm: Handwritten Notes → LaTeX
# Multi-stage: build React frontend, then run FastAPI backend
FROM node:20-slim AS frontend-builder

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --legacy-peer-deps || npm install

COPY frontend/ .
RUN npm run build

# Python + LaTeX runtime
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/
COPY backend/ backend/
COPY config/ config/
COPY run.py .
COPY --from=frontend-builder /build/dist frontend/dist

RUN mkdir -p /app/.cache /app/tmp && chown -R appuser:appuser /app
ENV TRANSFORMERS_NO_TF=1
ENV HF_HOME=/app/.cache
ENV TRANSFORMERS_CACHE=/app/.cache
ENV TMPDIR=/app/tmp

# Support both direct Docker (port 8000) and HF Spaces (port 7860)
ENV PORT=7860

USER appuser

EXPOSE 7860
EXPOSE 8000

CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
