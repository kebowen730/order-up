FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv (blazingly fast!)
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Run producer
CMD ["uv", "run", "python", "producer.py"]

