# Migration to uv

We've migrated to modern Python tooling with **uv** while maintaining backwards compatibility.

## What Changed?

**Before:**
```bash
pip install -r requirements.txt
python producer.py
```

**After:**
```bash
uv sync
uv run python producer.py
```

**Benefits**: 10-100x faster, lock files, better dependency resolution

## New Files

- `pyproject.toml` - Project metadata + dependencies
- `uv.lock` - Lock file (like package-lock.json)
- `.python-version` - Python version pinning

## For New Users

### Recommended (Modern)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd producer-python
uv sync
uv run python producer.py
```

### Legacy (Still Works)
```bash
cd producer-python
pip install -r requirements.txt
python producer.py
```

## For Existing Users

### Switch to uv
```bash
rm -rf venv/
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run python producer.py
```

### Keep using pip
```bash
# Nothing changes - requirements.txt still works
pip install -r requirements.txt
python producer.py
```

## For CI/CD

### Before
```yaml
- run: pip install -r requirements.txt
```

### After
```yaml
- uses: astral-sh/setup-uv@v1
- run: uv sync --frozen
- run: uv run python producer.py
```

**Speed improvement**: ~5-10x faster!

## Makefile Support

```bash
make install         # Uses uv (fallback to pip)
make install-legacy  # Forces pip
make run             # Auto-detects
```

## Resources

- `README-UV.md` - Why uv?
- https://docs.astral.sh/uv/

**TL;DR**: We support modern Python tooling (uv) while maintaining backwards compatibility with pip!
