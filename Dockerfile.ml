FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ML code
COPY ml/ ml/

# Create necessary directories
RUN mkdir -p ml/models ml/data

# Set environment variables
ENV PYTHONPATH=/app

# Start the ML training service
CMD ["python", "-m", "ml.training.train"] 