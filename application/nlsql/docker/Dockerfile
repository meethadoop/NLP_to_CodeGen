FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ /app/src/
COPY setup.py .

# Install the package in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p exports logs data

# Expose port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app/src

# Run the application
CMD ["uvicorn", "nlsql.service.api:app", "--host", "0.0.0.0", "--port", "8000"]
