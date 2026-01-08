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

To regenerate the data tables from Unicode data files (already downloaded in `tools/data/`):

```bash
# Regenerate confusables map from tools/data/confusables.txt
python3 tools/generate_confusables.py

# Regenerate script ranges from tools/data/Scripts.txt
python3 tools/generate_scripts.py

# Regenerate grapheme break data from tools/data/GraphemeBreakProperty.txt
python3 tools/generate_grapheme_data.py
```

**Note:** Unicode data files are already included. To download the latest Unicode version, delete the files in `tools/data/` and the generators will fetch them automatically.

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

If you modify core logic, please manually test performance (benchmarks suite to be added):

```python
import time
import indium

# Example: Benchmark skeleton()
text = "pаypal.com" * 100
start = time.perf_counter()
for _ in range(10_000):
    indium.skeleton(text)
elapsed = time.perf_counter() - start
print(f"skeleton: {elapsed*1000/10_000:.3f} ms/op")
```
