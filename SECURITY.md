# Security Policy

## Threat Model

`indium` is designed to detect and sanitize common text-based attack vectors.

### In Scope
- **Invisible Character Attacks:** Detects Zero Width Spaces, Control Characters, and Bidi overrides used to hide payloads.
- **Homograph Attacks (1-to-1):** Detects characters that look identical to Latin prototypes (e.g., Cyrillic 'а' vs Latin 'a').
- **Mixed Script Spoofing:** Detects when multiple scripts are mixed within a single word token.
- **Grapheme Manipulation:** Prevents broken rendering of emoji sequences and combining marks.

### Out of Scope / Limitations
- **Sequence-to-Character Spoofing (N-to-M):** `indium` normalizes character-by-character. It does **not** detect homoglyphs where a sequence of characters looks like a single target character (e.g., `rn` looking like `m`).
- **OCR / Visual Rendering:** `indium` does not render text to pixels. It relies on Unicode data tables. If a font renders two distinct characters identically, `indium` may not know they look alike unless Unicode TR39 explicitly maps them.
- **Cryptographic Verification:** `indium` is a heuristic inspection tool, not a cryptographic signature verifier.

## Reporting a Vulnerability

Please report security issues via GitHub Issues or email the maintainer directly if sensitive.
