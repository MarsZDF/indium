"""Elemental Indium: Text inspection, invisible characters, and integrity validation.

Zero-dependency Python library for:
- Detecting and sanitizing invisible characters
- Detecting visual spoofing via homoglyphs
- Safe grapheme-aware text operations

Modules:
    invisibles: Reveal and sanitize invisible characters
    spoofing: Detect homoglyphs and mixed scripts
    segments: Grapheme-aware text slicing

Example:
    >>> import indium
    >>> indium.sanitize("hello\\u200Bworld")
    'helloworld'
    >>> indium.skeleton("pаypal")  # Cyrillic 'а'
    'paypal'
    >>> indium.safe_truncate("👨‍👩‍👧test", 2)
    '👨\u200d👩\u200d👧t'
"""

# Public API exports
import unicodedata

from . import invisibles, segments, spoofing
from ._exceptions import IndiumError, InvalidTextError, TruncationError

# Import commonly used functions to top level
from .invisibles import count_by_category, detect_invisibles, reveal, sanitize
from .segments import count_graphemes, grapheme_slice, iter_graphemes, safe_truncate
from .spoofing import detect_confusables, get_script_blocks, is_mixed_script, skeleton

__version__ = "1.0.0"
unicode_version = unicodedata.unidata_version

__all__ = [
    # Metadata
    "unicode_version",
    # Modules
    "invisibles",
    "spoofing",
    "segments",
    # Exceptions
    "IndiumError",
    "InvalidTextError",
    "TruncationError",
    # invisibles functions
    "reveal",
    "sanitize",
    "detect_invisibles",
    "count_by_category",
    # spoofing functions
    "skeleton",
    "is_mixed_script",
    "get_script_blocks",
    "detect_confusables",
    # segments functions
    "safe_truncate",
    "count_graphemes",
    "grapheme_slice",
    "iter_graphemes",
]
