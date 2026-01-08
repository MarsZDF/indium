"""Invisible character detection and sanitization.

This module provides functions to reveal, sanitize, and analyze invisible
characters in Unicode text. Useful for security validation, log analysis,
and preventing invisible character attacks.
"""

from typing import Final

from ._unicode_data import (
    get_category,
    get_unicode_name,
    is_invisible,
    is_whitespace,
)

# Special invisible characters requiring specific handling
ZWJ: Final[str] = '\u200D'  # ZERO WIDTH JOINER (essential for emoji)
ZWNJ: Final[str] = '\u200C'  # ZERO WIDTH NON-JOINER
ZWSP: Final[str] = '\u200B'  # ZERO WIDTH SPACE
SOFT_HYPHEN: Final[str] = '\u00AD'  # SOFT HYPHEN

# Bidi control characters (security risk - homograph attacks)
BIDI_CONTROLS: Final[frozenset[str]] = frozenset({
    '\u202A',  # LEFT-TO-RIGHT EMBEDDING
    '\u202B',  # RIGHT-TO-LEFT EMBEDDING
    '\u202C',  # POP DIRECTIONAL FORMATTING
    '\u202D',  # LEFT-TO-RIGHT OVERRIDE
    '\u202E',  # RIGHT-TO-LEFT OVERRIDE
    '\u2066',  # LEFT-TO-RIGHT ISOLATE
    '\u2067',  # RIGHT-TO-LEFT ISOLATE
    '\u2068',  # FIRST STRONG ISOLATE
    '\u2069',  # POP DIRECTIONAL ISOLATE
})


def reveal(text: str, *, substitute: str = "␣", format: str = "unicode") -> str:
    """Replace invisible characters with visible markers.

    Args:
        text: Input string
        substitute: Marker for standard whitespace (default: "␣")
        format: Output format - "unicode" for <U+200B>, "hex" for \\u200b,
                "name" for ZERO WIDTH SPACE

    Returns:
        String with invisibles replaced by visible markers

    Raises:
        ValueError: If format is not recognized

    Examples:
        >>> reveal("hello\\u200Bworld")
        'hello<U+200B>world'
        >>> reveal("hello\\u200Bworld", format="hex")
        'hello\\\\u200bworld'
        >>> reveal("hello\\u200Bworld", format="name")
        'hello<ZERO WIDTH SPACE>world'
        >>> reveal("hello world", substitute="·")
        'hello·world'
    """
    if format not in ("unicode", "hex", "name"):
        raise ValueError(f"Invalid format: {format!r}. Must be 'unicode', 'hex', or 'name'")

    result: list[str] = []

    for char in text:
        if is_whitespace(char):
            # Standard whitespace - use substitute marker
            result.append(substitute)
        elif is_invisible(char):
            # Invisible character - format based on format parameter
            if format == "unicode":
                codepoint = ord(char)
                result.append(f"<U+{codepoint:04X}>")
            elif format == "hex":
                codepoint = ord(char)
                result.append(f"\\u{codepoint:04x}")
            else:  # format == "name"
                name = get_unicode_name(char, f"U+{ord(char):04X}")
                result.append(f"<{name}>")
        else:
            # Regular character - keep as-is
            result.append(char)

    return ''.join(result)


def sanitize(text: str, *, schema: str = "strict", preserve_zwj: bool = False) -> str:
    """Remove invisible characters while preserving legitimate whitespace.

    Args:
        text: Input string
        schema: Sanitization schema:
                - "strict": Remove all invisibles except standard whitespace
                - "permissive": Keep ZWJ for emoji sequences
        preserve_zwj: If True, preserve ZWJ for emoji (overrides schema)

    Returns:
        Cleaned string with invisible characters removed

    Raises:
        ValueError: If schema is not recognized

    Examples:
        >>> sanitize("hello\\u200Bworld")
        'helloworld'
        >>> sanitize("hello world")  # Preserves spaces
        'hello world'
        >>> sanitize("family👨\\u200D👩\\u200D👧", schema="permissive")
        'family👨\\u200d👩\\u200d👧'
        >>> sanitize("family👨\\u200D👩\\u200D👧", preserve_zwj=True)
        'family👨\\u200d👩\\u200d👧'
    """
    if schema not in ("strict", "permissive"):
        raise ValueError(f"Invalid schema: {schema!r}. Must be 'strict' or 'permissive'")

    keep_zwj = preserve_zwj or (schema == "permissive")
    result: list[str] = []

    for char in text:
        # Always keep standard whitespace
        if is_whitespace(char) or char == ZWJ and keep_zwj:
            result.append(char)
        # Remove all other invisible characters
        elif is_invisible(char):
            continue
        # Keep all visible characters
        else:
            result.append(char)

    return ''.join(result)


def detect_invisibles(text: str) -> list[tuple[int, str, str]]:
    """Find all invisible characters and their positions.

    Args:
        text: Input string to analyze

    Returns:
        List of (position, character, unicode_name) tuples for each invisible
        character found. Standard whitespace is NOT included.

    Examples:
        >>> detect_invisibles("hello\\u200Bworld")
        [(5, '\\u200b', 'ZERO WIDTH SPACE')]
        >>> detect_invisibles("hello world")  # Space is not invisible
        []
        >>> text = "a\\u202Eb\\u200Bc"
        >>> invisibles = detect_invisibles(text)
        >>> len(invisibles)
        2
        >>> invisibles[0][2]  # Unicode name
        'RIGHT-TO-LEFT OVERRIDE'
    """
    result: list[tuple[int, str, str]] = []

    for pos, char in enumerate(text):
        if not is_whitespace(char) and is_invisible(char):
            name = get_unicode_name(char, f"U+{ord(char):04X}")
            result.append((pos, char, name))

    return result


def count_by_category(text: str) -> dict[str, int]:
    """Count characters by Unicode category.

    Useful for analyzing text composition and identifying potential issues.

    Args:
        text: Input string to analyze

    Returns:
        Dict mapping category code to count

    Examples:
        >>> count_by_category("hello")
        {'Ll': 5}
        >>> count_by_category("Hello World!")
        {'Lu': 2, 'Ll': 8, 'Zs': 1, 'Po': 1}
        >>> result = count_by_category("test\\u200B")
        >>> result['Cf']  # Format category (invisible)
        1
    """
    counts: dict[str, int] = {}

    for char in text:
        category = get_category(char)
        counts[category] = counts.get(category, 0) + 1

    return counts
