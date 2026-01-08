"""Grapheme-aware text operations without regex library dependency.

This module provides safe text slicing and truncation that respects grapheme
cluster boundaries. Prevents breaking emoji sequences, combining character
sequences, and other multi-codepoint visual units.

LIMITATION: This is a heuristic implementation covering common cases (emoji,
combining marks, skin tones, flags). It is NOT a full UAX#29 implementation.
"""

import unicodedata
from typing import Iterator, Optional

from ._exceptions import TruncationError
from ._unicode_data import is_combining

# Zero Width Joiner - used in emoji sequences
ZWJ: str = '\u200D'

# Hangul Constants (UAX #29)
HANGUL_L_START = 0x1100
HANGUL_L_END = 0x115F
HANGUL_V_START = 0x1160
HANGUL_V_END = 0x11A7
HANGUL_T_START = 0x11A8
HANGUL_T_END = 0x11FF
HANGUL_SYLLABLE_START = 0xAC00
HANGUL_SYLLABLE_END = 0xD7A3


def safe_truncate(text: str, max_graphemes: int) -> str:
    """Truncate text to max grapheme clusters, not code points.

    Ensures cut doesn't break:
    - Emoji sequences (ZWJ, skin tone modifiers)
    - Combining character sequences (base + marks)
    - Regional indicator pairs (flag emoji)

    Args:
        text: Input string
        max_graphemes: Maximum number of visual units (grapheme clusters)

    Returns:
        Truncated string at valid grapheme boundary

    Raises:
        ValueError: If max_graphemes is negative

    Examples:
        >>> safe_truncate("hello", 3)
        'hel'
        >>> safe_truncate("café", 3)  # é is one grapheme
        'caf'
        >>> safe_truncate("👨‍👩‍👧", 1)  # Family emoji is one grapheme
        '👨\u200d👩\u200d👧'
        >>> safe_truncate("hello👋🏽world", 6)  # Waving hand with skin tone
        'hello👋🏽'
    """
    if max_graphemes < 0:
        raise ValueError(f"max_graphemes must be non-negative, got {max_graphemes}")

    if max_graphemes == 0:
        return ""

    grapheme_count = 0
    pos = 0

    while pos < len(text) and grapheme_count < max_graphemes:
        # Find end of current grapheme
        grapheme_end = _find_grapheme_end(text, pos)
        pos = grapheme_end
        grapheme_count += 1

    return text[:pos]


def count_graphemes(text: str) -> int:
    """Count grapheme clusters (visual units) in text.

    Args:
        text: Input string

    Returns:
        Number of grapheme clusters

    Examples:
        >>> count_graphemes("hello")
        5
        >>> count_graphemes("café")  # é = e + combining acute
        4
        >>> count_graphemes("👨‍👩‍👧")  # Family emoji
        1
        >>> count_graphemes("hello👋🏽")  # Waving with skin tone
        6
    """
    count = 0
    pos = 0

    while pos < len(text):
        grapheme_end = _find_grapheme_end(text, pos)
        count += 1
        pos = grapheme_end

    return count


def grapheme_slice(text: str, start: int, end: Optional[int] = None) -> str:
    """Slice text by grapheme indices, not code points.

    Args:
        text: Input string
        start: Start grapheme index (inclusive)
        end: End grapheme index (exclusive). If None, slice to end

    Returns:
        Substring from start to end grapheme indices

    Raises:
        ValueError: If start is negative or end < start

    Examples:
        >>> grapheme_slice("hello", 1, 4)
        'ell'
        >>> grapheme_slice("café", 0, 3)
        'caf'
        >>> grapheme_slice("👨‍👩‍👧test", 1, 3)
        'te'
    """
    if start < 0:
        raise ValueError(f"start must be non-negative, got {start}")

    if end is not None and end < start:
        raise ValueError(f"end ({end}) must be >= start ({start})")

    # Find start position in code points
    grapheme_count = 0
    start_pos = 0

    while start_pos < len(text) and grapheme_count < start:
        grapheme_end = _find_grapheme_end(text, start_pos)
        start_pos = grapheme_end
        grapheme_count += 1

    # If we ran out of text before reaching start, return empty
    if start_pos >= len(text):
        return ""

    # If no end specified, return from start to end of text
    if end is None:
        return text[start_pos:]

    # Find end position in code points
    end_pos = start_pos
    while end_pos < len(text) and grapheme_count < end:
        grapheme_end = _find_grapheme_end(text, end_pos)
        end_pos = grapheme_end
        grapheme_count += 1

    return text[start_pos:end_pos]


def iter_graphemes(text: str) -> Iterator[str]:
    """Iterate over grapheme clusters.

    Args:
        text: Input string

    Yields:
        Individual grapheme clusters

    Examples:
        >>> list(iter_graphemes("hello"))
        ['h', 'e', 'l', 'l', 'o']
        >>> list(iter_graphemes("café"))
        ['c', 'a', 'f', 'é']
        >>> list(iter_graphemes("a👋🏽b"))
        ['a', '👋🏽', 'b']
    """
    pos = 0

    while pos < len(text):
        grapheme_end = _find_grapheme_end(text, pos)
        yield text[pos:grapheme_end]
        pos = grapheme_end


# Internal helper: Find end of grapheme cluster starting at pos
def _find_grapheme_end(text: str, pos: int) -> int:
    """Find the end position of the grapheme cluster starting at pos.

    Implements a subset of Unicode TR29 (Extended Grapheme Clusters).
    Handles common cases but not all edge cases.

    Args:
        text: Input string
        pos: Start position of grapheme

    Returns:
        Position after the end of the grapheme cluster
    """
    if pos >= len(text):
        return pos

    # Start with first character
    end = pos + 1

    # Continue while we're not at a grapheme boundary
    while end < len(text) and not _is_grapheme_boundary(text, end):
        end += 1

    return end


def _is_grapheme_boundary(text: str, pos: int) -> bool:
    """Check if position is a valid grapheme boundary.

    Implements grapheme boundary rules from Unicode TR29.
    This is a heuristic covering common cases, not a complete implementation.

    Args:
        text: Input string
        pos: Position to check

    Returns:
        True if position is a valid grapheme boundary
    """
    if pos >= len(text):
        return True

    if pos == 0:
        return True

    current = text[pos]
    previous = text[pos - 1]

    # Rule GB3: CR x LF
    if previous == '\r' and current == '\n':
        return False

    # Rule GB4/GB5: Control characters break (unless handled by GB3)
    # We treat standard Control/Format as boundaries unless they are extending marks
    # But for a simple library, let's stick to specific checks
    
    # Don't break before combining marks (Mn, Mc, Me)
    if is_combining(current):
        return False

    # Don't break within ZWJ sequences (emoji ligatures)
    # Example: 👨‍👩‍👧 (family) = man + ZWJ + woman + ZWJ + girl
    if previous == ZWJ:
        return False
    if current == ZWJ:
        return False

    # Don't break emoji modifier sequences (skin tone)
    # Skin tone modifiers: U+1F3FB-U+1F3FF
    if '\U0001F3FB' <= current <= '\U0001F3FF':
        return False

    # Don't break regional indicator pairs (flag emoji)
    # Flags are pairs of regional indicators: U+1F1E6-U+1F1FF
    # Example: 🇺🇸 = U+1F1FA + U+1F1F8
    if _is_regional_indicator(previous) and _is_regional_indicator(current):
        return False

    # Don't break variation selectors (U+FE00-U+FE0F)
    # These modify the presentation of the previous character
    if '\uFE00' <= current <= '\uFE0F':
        return False

    # Don't break emoji presentation selector (U+FE0F)
    # Used to force emoji rendering of characters that can be text or emoji
    if current == '\uFE0F':
        return False
        
    # Hangul Syllable logic (UAX #29 GB6, GB7, GB8)
    # L = Choseong, V = Jungseong, T = Jongseong, LV, LVT
    
    # Check simple L, V, T ranges
    prev_code = ord(previous)
    curr_code = ord(current)
    
    is_prev_L = HANGUL_L_START <= prev_code <= HANGUL_L_END
    is_curr_L = HANGUL_L_START <= curr_code <= HANGUL_L_END
    is_curr_V = HANGUL_V_START <= curr_code <= HANGUL_V_END
    
    # GB6: L x (L|V|LV|LVT)
    if is_prev_L:
        if is_curr_L: return False # L x L
        if is_curr_V: return False # L x V
        if HANGUL_SYLLABLE_START <= curr_code <= HANGUL_SYLLABLE_END: return False # L x LV or L x LVT
        
    # Partial implementation for common Hangul composition
    # (Full implementation would require complete properties for all Hangul syllables)

    return True


def _is_regional_indicator(char: str) -> bool:
    """Check if character is a regional indicator (used for flags).

    Args:
        char: Single character

    Returns:
        True if character is in regional indicator range
    """
    if len(char) != 1:
        return False

    return '\U0001F1E6' <= char <= '\U0001F1FF'
