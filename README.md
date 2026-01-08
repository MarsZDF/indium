# Elemental Indium

Zero-dependency Python library for text **IN**spection, **IN**visible character detection, and **IN**tegrity validation.

## Installation

```bash
pip install elemental-indium
```

## Quick Start

```python
import indium

# Detect invisible characters
text = "hello\u200Bworld"  # Contains ZERO WIDTH SPACE
indium.reveal(text)  # "hello<U+200B>world"
indium.sanitize(text)  # "helloworld"

# Detect visual spoofing
domain = "pаypal.com"  # Cyrillic 'а' looks like Latin 'a'
indium.skeleton(domain)  # "paypal.com"
indium.is_mixed_script(domain)  # True

# Safe text truncation
emoji = "👨‍👩‍👧test"  # Family emoji + text
indium.safe_truncate(emoji, 2)  # "👨‍👩‍👧t" (doesn't break emoji)
indium.count_graphemes(emoji)  # 5 (not 9 code points)
```

## Features

- **Zero runtime dependencies** - Pure Python, stdlib only
- **Standards Compliant**:
  - **UAX #29** - Grapheme Cluster Boundaries (for emoji/text segmentation)
  - **TR39** - Unicode Security Mechanisms (for confusable detection)
- **Data Driven** - Powered by official Unicode Consortium datasets (Scripts & Confusables)
- **Type-safe** - Full `mypy --strict` compliance
- **Defensive** - Handles malformed Unicode gracefully
- **Python 3.9+** - Compatible with all modern Python versions

## Development

The library uses pre-generated lookup tables for performance and stability. To update these tables with the latest Unicode data:

```bash
# Download and regenerate data tables
python3 tools/generate_confusables.py
python3 tools/generate_scripts.py
```

## Documentation

Full documentation coming soon.

## Compatibility Warning

Since `indium` relies on the standard library's `unicodedata` module, the exact behavior (especially regarding new emoji or very recent Unicode characters) depends on the Python version you are running.

- **Python 3.9**: Unicode 13.0
- **Python 3.10**: Unicode 13.0
- **Python 3.11**: Unicode 14.0
- **Python 3.12**: Unicode 15.0

You can check the active Unicode version at runtime:
```python
print(indium.unicode_version)  # e.g., '15.0.0'
```

## License

MIT
