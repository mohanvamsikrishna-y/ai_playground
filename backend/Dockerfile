FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (app directory becomes /app/app)
COPY app/ ./app/

EXPOSE 8000

# Run uvicorn from /app, which will find app.main module
# Cloud Run sets PORT env var, default to 8000 for local development
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
