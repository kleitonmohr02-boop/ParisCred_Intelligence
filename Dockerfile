# ParisCred AI - Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV DATABASE_PATH=pariscred.db

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "main.py"]