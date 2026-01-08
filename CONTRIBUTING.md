# Contributing to Elemental Indium

Thank you for your interest in contributing to `elemental-indium`! We strive for high standards in security, correctness, and data integrity.

## Development Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/MarsZDF/indium.git
    cd indium
    ```

2.  Install dependencies (including dev tools):
    ```bash
    pip install -e ".[dev,test]"
    ```

## Unicode Data Updates

This library relies on official Unicode Consortium data. **Do not edit `src/indium/_confusables.py` or `_scripts_data.py` manually.**

To update the data tables:

```bash
# This will download the latest data from unicode.org and regenerate the python modules
python3 tools/generate_confusables.py
python3 tools/generate_scripts.py
```

## Testing

We use `pytest` and `hypothesis` for property-based testing.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=indium
```

**Note:** `indium` behavior depends on the Python version (which determines the underlying `unicodedata` version). We support Python 3.9+.

## Code Quality

We enforce strict linting and type checking.

```bash
# Linting
ruff check .

# Type Checking
mypy src/indium --strict
```

## Benchmarks

If you modify core logic, please run benchmarks to ensure no regression in the "Fast Path" optimizations.

```bash
python3 benchmarks/bench_core.py
```
