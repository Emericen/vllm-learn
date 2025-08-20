FROM python:3.10-slim

# Install system dependencies including C++ compiler
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using uv
RUN uv pip install --system -r requirements.txt

# Additional dependencies already in requirements.txt

# Copy application files
COPY main.py .


# Expose port for WebSocket
EXPOSE 8001

# Run the Python application directly
CMD ["python", "main.py"]