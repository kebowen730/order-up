.PHONY: help install install-legacy run test lint clean

help:
	@echo "Producer Commands"
	@echo "================="
	@echo ""
	@echo "make install        - Install dependencies with uv (modern)"
	@echo "make install-legacy - Install with pip (if uv not available)"
	@echo "make run            - Run the producer"
	@echo "make test           - Run tests and verification"
	@echo "make lint           - Run ruff linter"
	@echo "make clean          - Clean Python cache files"
	@echo ""

install:
	@echo "📦 Installing with uv..."
	@command -v uv >/dev/null 2>&1 || (echo "❌ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" && exit 1)
	uv sync

install-legacy:
	@echo "📦 Installing with pip (legacy)..."
	pip install -r requirements.txt

run:
	@command -v uv >/dev/null 2>&1 && uv run python producer.py || python producer.py

test:
	@echo "🧪 Running producer test..."
	./test_producer.sh

lint:
	@command -v uv >/dev/null 2>&1 && uv run ruff check . || echo "⚠️  uv not installed, skipping lint"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .venv 2>/dev/null || true
	@echo "✅ Cleaned Python cache files"

