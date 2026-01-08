"""Grapheme-aware text operations without regex library dependency.

This module provides safe text slicing and truncation that respects grapheme
cluster boundaries. Prevents breaking emoji sequences, combining character
sequences, and other multi-codepoint visual units.

Implementation: UAX #29 (Unicode Text Segmentation)
"""

import bisect
from collections.abc import Iterator
from functools import lru_cache
from typing import Optional

from ._grapheme_data import (
    CONTROL,
    CR,
    EXTEND,
    EXTENDED_PICTOGRAPHIC,
    GRAPHEME_BREAK_RANGES,
    INCB_CONSONANT,
    INCB_EXTEND,
    INCB_LINKER,
    LF,
    LV,
    LVT,
    PREPEND,
    REGIONAL_INDICATOR,
    SPACINGMARK,
    ZWJ,
    L,
    T,
    V,
)


@lru_cache(maxsize=4096)
def _get_break_property(codepoint: int) -> int:
    """Get Grapheme_Cluster_Break property for a code point."""
    # Binary search in the RLE table
    # index-1 gives the range containing codepoint (or starting before it)
    idx = bisect.bisect_right(GRAPHEME_BREAK_RANGES, (codepoint, 999))
    if idx == 0:
        return 0  # Should not happen if table covers 0

    start, prop = GRAPHEME_BREAK_RANGES[idx - 1]
    return prop


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

    Implements Unicode TR29 (Grapheme Cluster Boundaries).

    Args:
        text: Input string
        pos: Position to check

    Returns:
        True if position is a valid grapheme boundary
    """
    if pos == 0 or pos >= len(text):
        return True

    curr_char = text[pos]
    prev_char = text[pos - 1]

    curr_prop = _get_break_property(ord(curr_char))
    prev_prop = _get_break_property(ord(prev_char))

    # GB3: CR x LF
    if prev_prop == CR and curr_prop == LF:
        return False

    # GB4: (Control | CR | LF) ÷
    if prev_prop in (CONTROL, CR, LF):
        return True

    # GB5: ÷ (Control | CR | LF)
    if curr_prop in (CONTROL, CR, LF):
        return True

    # GB6: L x (L | V | LV | LVT)
    if prev_prop == L and curr_prop in (L, V, LV, LVT):
        return False

    # GB7: (LV | V) x (V | T)
    if prev_prop in (LV, V) and curr_prop in (V, T):
        return False

    # GB8: (LVT | T) x T
    if prev_prop in (LVT, T) and curr_prop == T:
        return False

    # GB9: x (Extend | ZWJ)
    # Note: InCB_Linker and InCB_Extend must also be treated as Extend for GB9
    if curr_prop in (EXTEND, ZWJ, INCB_EXTEND, INCB_LINKER):
        return False

    # GB9a: x SpacingMark
    if curr_prop == SPACINGMARK:
        return False

    # GB9b: Prepend x
    if prev_prop == PREPEND:
        return False

    # GB9c: \p{InCB=Linker} [ \p{InCB=Extend} \p{InCB=Linker} \p{Zwj} ]* x \p{InCB=Consonant}
    # Restriction: The Linker itself must be part of a valid syllable, i.e., preceded by Consonant.
    # This fixes failures where 'a' + Virama + 'Ta' breaks (because 'a' is not InCB Consonant).
    if curr_prop == INCB_CONSONANT:
        # 1. Scan backwards for Linker
        i = pos - 1
        found_linker = False
        linker_index = -1

        while i >= 0:
            prop = _get_break_property(ord(text[i]))
            if prop == INCB_LINKER:
                found_linker = True
                linker_index = i
                break
            if prop not in (EXTEND, ZWJ, INCB_EXTEND, INCB_LINKER):
                break  # Sequence broken before finding Linker
            i -= 1

        if found_linker:
            # 2. Verify Linker is attached to a Consonant
            # Scan backwards from Linker skipping Extend/ZWJ/Linker
            j = linker_index - 1
            valid_base = False
            while j >= 0:
                prop_j = _get_break_property(ord(text[j]))
                if prop_j == INCB_CONSONANT:
                    valid_base = True
                    break
                if prop_j not in (EXTEND, ZWJ, INCB_EXTEND, INCB_LINKER):
                    break # Hit start of cluster or invalid char
                j -= 1

            if valid_base:
                return False

    # GB11: \p{Extended_Pictographic} Extend* ZWJ x \p{Extended_Pictographic}
    if prev_prop == ZWJ and curr_prop == EXTENDED_PICTOGRAPHIC:
        # Scan backwards to see if ZWJ is preceded by Extended_Pictographic + Extend*
        i = pos - 2
        while i >= 0:
            prop = _get_break_property(ord(text[i]))
            if prop == EXTENDED_PICTOGRAPHIC:
                return False
            # Treat InCB properties as Extend for this rule too?
            # UAX #29 says "Extend". InCB_Extend and InCB_Linker ARE Extend.
            if prop not in (EXTEND, INCB_EXTEND, INCB_LINKER):
                break
            i -= 1

    # GB12/GB13: Regional_Indicator sequence
    if prev_prop == REGIONAL_INDICATOR and curr_prop == REGIONAL_INDICATOR:
        # We need to count RI characters backwards from pos
        # If count is odd, it's a valid pair (break after second).
        # If count is even, we are in middle of new pair (no break).
        # The rule effectively says: "Do not break within a pair".
        # A pair starts at an even offset from the start of the RI sequence.

        ri_count = 0
        i = pos - 1
        while i >= 0 and _get_break_property(ord(text[i])) == REGIONAL_INDICATOR:
            ri_count += 1
            i -= 1

        # If we have seen an odd number of RIs before 'curr',
        # then 'prev' and 'curr' form a pair.
        if ri_count % 2 == 1:
            return False

    # GB999: Any ÷ Any
    return True
