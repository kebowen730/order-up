# Why uv? 🚀

**uv** is a modern, blazingly fast Python package installer created by Astral (makers of ruff).

## Key Benefits

1. **⚡ Speed**: 10-100x faster than pip
2. **🔒 Reliable**: Lock files for reproducible builds
3. **🎯 Modern**: Uses `pyproject.toml` (PEP 621)
4. **🔄 Compatible**: Works with existing tools

## Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with homebrew
brew install uv
```

## Usage

```bash
# Install dependencies
uv sync

# Run with managed environment
uv run python producer.py

# Add a new dependency
uv add requests
```

## Comparison

### Old Way (pip)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Slow, no lock file
python producer.py
```

### New Way (uv)
```bash
uv sync          # Fast, with lock file
uv run python producer.py
```

## Backwards Compatibility

Don't have uv? No problem! We keep `requirements.txt`:

```bash
pip install -r requirements.txt
python producer.py
```

## Why This Matters

1. **Deterministic Builds**: Lock file ensures same versions everywhere
2. **Faster CI/CD**: 10x faster dependency installation
3. **Better Reliability**: Proper dependency resolution
4. **Modern Standard**: Industry is moving to pyproject.toml

## Resources

- **uv GitHub**: https://github.com/astral-sh/uv
- **uv Docs**: https://docs.astral.sh/uv/

**TL;DR**: uv is faster, more reliable, and more modern than pip. But if you prefer pip, that still works too!
