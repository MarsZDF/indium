# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-01-08

### Added
- **Production release** of elemental-indium
- **Invisibles module** (`indium.invisibles`):
  - `reveal()` - Replace invisible characters with visible markers
  - `sanitize()` - Remove invisible characters while preserving whitespace
  - `detect_invisibles()` - Find all invisible characters and their positions
  - `count_by_category()` - Count characters by Unicode category
- **Spoofing module** (`indium.spoofing`):
  - `skeleton()` - Convert text to visual skeleton (canonical confusable form)
  - `is_mixed_script()` - Detect mixed script usage (e.g., Latin + Cyrillic)
  - `get_script_blocks()` - Identify script blocks in text
  - `detect_confusables()` - Find characters that look like target script but aren't
- **Segments module** (`indium.segments`):
  - `safe_truncate()` - Truncate text without breaking grapheme clusters
  - `count_graphemes()` - Count grapheme clusters (visual units) in text
  - `grapheme_slice()` - Slice text by grapheme indices
  - `iter_graphemes()` - Iterate over grapheme clusters
- **Zero runtime dependencies** - Pure Python stdlib only
- **Type safety** - Full mypy --strict compliance
- **Comprehensive test suite** - 98% code coverage with 893 tests
- **Standards compliance**:
  - UAX #29 (Grapheme Cluster Boundaries)
  - TR39 (Unicode Security Mechanisms)
- **Data-driven approach**:
  - Pre-generated lookup tables from official Unicode data
  - Binary search for O(log n) script detection
  - LRU caching for performance optimization
- **Python 3.9+ support** - Compatible with Python 3.9-3.13

### Security
- **Comprehensive confusables map (1,861 characters)** from Unicode TR39 covering homograph attacks:
  - **Mathematical alphabets**: 837 chars (bold, italic, script, fraktur, double-struck variants)
  - **Latin/Cyrillic confusables**: 54 chars (а, е, о, р, с, у, х, А, В, Е, К, М, Н, О, Р, С, Т, Х, etc.)
  - **Latin/Greek confusables**: 54 chars (α, ο, ν, ι, ρ, Α, Β, Ε, Ζ, Η, Ι, Κ, Μ, Ν, Ο, Ρ, Τ, Υ, Χ, etc.)
  - **Arabic/Hebrew**: 48 chars
  - **Latin extended variants**: 199 chars (IPA, phonetic extensions)
  - **Fullwidth forms**: 8 chars (ａ-ｚ, Ａ-Ｚ)
  - **Other scripts**: 618 chars
- Bidi control character detection and removal
- ZWJ (Zero Width Joiner) handling for emoji sequences

### Documentation
- Comprehensive README with examples
- CONTRIBUTING.md for developers
- SECURITY.md for responsible disclosure
- CI/CD workflows for automated testing and publishing

[Unreleased]: https://github.com/MarsZDF/indium/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/MarsZDF/indium/releases/tag/v1.0.0
