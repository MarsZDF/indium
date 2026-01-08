"""Unicode category helpers and utilities.

Private module providing low-level Unicode operations.
Zero external dependencies - stdlib only.
"""

import unicodedata
from typing import Final

# Whitespace characters (not considered invisible for our purposes)
WHITESPACE_CHARS: Final[frozenset[str]] = frozenset({' ', '\n', '\t', '\r', '\v', '\f'})

# Invisible Unicode categories
# Cf = Format characters (zero-width, bidi controls, etc.)
# Cc = Control characters (NULL, backspace, etc.)
# Co = Private use characters
INVISIBLE_CATEGORIES: Final[frozenset[str]] = frozenset({'Cf', 'Cc', 'Co'})


def is_invisible(char: str) -> bool:
    """Check if character is invisible (Format, Control, or Private Use).

    Args:
        char: Single character to check

    Returns:
        True if character is in Cf, Cc, or Co Unicode category

    Examples:
        >>> is_invisible('\u200B')  # ZERO WIDTH SPACE
        True
        >>> is_invisible('a')
        False
        >>> is_invisible(' ')  # Regular space is NOT invisible
        False
    """
    if len(char) != 1:
        raise ValueError(f"Expected single character, got {len(char)} characters")

    # Standard whitespace is NOT invisible
    if char in WHITESPACE_CHARS:
        return False

    category = unicodedata.category(char)
    return category in INVISIBLE_CATEGORIES


def is_combining(char: str) -> bool:
    """Check if character is a combining mark.

    Combining marks (accents, diacritics) attach to base characters.

    Args:
        char: Single character to check

    Returns:
        True if character has non-zero combining class

    Examples:
        >>> is_combining('\u0301')  # COMBINING ACUTE ACCENT
        True
        >>> is_combining('a')
        False
    """
    if len(char) != 1:
        raise ValueError(f"Expected single character, got {len(char)} characters")

    # combining() only returns Canonical Combining Class, which is 0 for many
    # combining characters (e.g., enclosing marks, Hebrew vowels).
    # We must check the category: Mn (Nonspacing), Mc (Spacing), Me (Enclosing)
    return unicodedata.category(char).startswith('M')


def is_whitespace(char: str) -> bool:
    r"""Check if character is standard whitespace.

    Args:
        char: Single character to check

    Returns:
        True if character is space, newline, tab, etc.

    Examples:
        >>> is_whitespace(' ')
        True
        >>> is_whitespace('\n')
        True
        >>> is_whitespace('\u200B')  # ZERO WIDTH SPACE is NOT standard whitespace
        False
    """
    if len(char) != 1:
        raise ValueError(f"Expected single character, got {len(char)} characters")

    return char in WHITESPACE_CHARS


def get_unicode_name(char: str, default: str = "<unnamed>") -> str:
    """Get Unicode character name.

    Args:
        char: Single character
        default: Default name if character has no name

    Returns:
        Unicode character name or default

    Examples:
        >>> get_unicode_name('a')
        'LATIN SMALL LETTER A'
        >>> get_unicode_name('\u200B')
        'ZERO WIDTH SPACE'
    """
    if len(char) != 1:
        raise ValueError(f"Expected single character, got {len(char)} characters")

    try:
        return unicodedata.name(char)
    except ValueError:
        return default


def get_category(char: str) -> str:
    """Get Unicode category for character.

    Args:
        char: Single character

    Returns:
        Two-letter category code (e.g., 'Ll', 'Cf', 'Cc')

    Examples:
        >>> get_category('a')
        'Ll'
        >>> get_category('\u200B')
        'Cf'
    """
    if len(char) != 1:
        raise ValueError(f"Expected single character, got {len(char)} characters")

    return unicodedata.category(char)
