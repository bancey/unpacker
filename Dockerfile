FROM python:3.11-slim

# Install system dependencies for archive extraction
# Note: Uses unrar-free (open source) instead of unrar (non-free)
# For full RAR5 support, you may need to manually install unrar-nonfree
RUN apt-get update && apt-get install -y \
    unrar-free \
    unzip \
    p7zip-full \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY config.py .
COPY unpacker.py .
COPY templates/ templates/
COPY static/ static/

# Create directory for config file
RUN mkdir -p /config

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH=/config/config.json

# Run the application
CMD ["python", "app.py"]
