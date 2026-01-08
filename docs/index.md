# Elemental Indium

Zero-dependency Python library for text **IN**spection, **IN**visible character detection, and **IN**tegrity validation.

Protect your application from invisible character attacks, visual spoofing (homoglyphs), and text processing bugs caused by complex Unicode sequences.

## Installation

```bash
pip install elemental-indium
```

## Why Indium?

- **Security First**: Detect homoglyph attacks and invisible characters used in phishing or prompt injection.
- **Zero Runtime Dependencies**: Pure Python, uses standard library only.
- **Standards Compliant**: Full UAX #29 Grapheme Cluster Boundary support and TR39 Security Mechanisms.
- **Defensive**: Handles malformed Unicode gracefully without crashing.

## Quick Start

```python
import indium

# Reveal the invisible
text = "hello\u200Bworld"
indium.reveal(text)  # "hello<U+200B>world"

# Stop the spoofing
domain = "pаypal.com"  # Uses Cyrillic 'а'
indium.is_mixed_script(domain)  # True
indium.skeleton(domain)         # "paypal.com"

# Safe truncation (don't break emojis)
emoji = "👨‍👩‍👧test"
indium.safe_truncate(emoji, 2)  # "👨‍👩‍👧t"
```
