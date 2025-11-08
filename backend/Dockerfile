# Use Python 3.13 base image (as required by pyproject.toml)
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency installation
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Export requirements from uv.lock and install into system Python
RUN uv export --frozen --no-hashes > requirements.txt && \
    uv pip install --system -r requirements.txt

# Install LangGraph CLI
RUN pip install --no-cache-dir "langgraph-cli[inmem]"

# Copy application files
COPY langgraph.json ./
COPY graph.py ./
COPY app.py ./
COPY prompts/ ./prompts/
COPY vectorstore/ ./vectorstore/

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8123

# Default command (can be overridden in docker-compose.yml)
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "8123"]
