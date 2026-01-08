"""Visual spoofing detection via homoglyphs and mixed scripts.

This module provides functions to detect and normalize visually confusable
characters that could be used in phishing attacks, domain spoofing, or
other security vulnerabilities.
"""

import bisect
import unicodedata
from functools import lru_cache

from ._confusables import CONFUSABLES
from ._scripts_data import SCRIPT_RANGES


def skeleton(text: str) -> str:
    """Convert text to visual skeleton (canonical confusable form).

    Maps confusable characters to their Latin prototypes:
    - Cyrillic 'а' (U+0430) → Latin 'a'
    - Greek 'ο' (U+03BF) → Latin 'o'
    - Fullwidth 'ａ' (U+FF41) → Latin 'a'

    Uses NFKC normalization + confusables map (~70 chars).

    Args:
        text: Input string to normalize

    Returns:
        Normalized string with confusables replaced by Latin equivalents

    Examples:
        >>> skeleton("pаypal")  # Cyrillic 'а'
        'paypal'
        >>> skeleton("gοοgle")  # Greek 'ο'
        'google'
        >>> skeleton("ｆａｃｅｂｏｏｋ")  # Fullwidth
        'facebook'
        >>> skeleton(skeleton("test"))  # Idempotent
        'test'
    """
    # Fast path: ASCII strings are already normalized and "Latin"
    if text.isascii():
        return text

    # Step 1: Apply NFKC normalization (compatibility decomposition)
    # This handles many mathematical/styled variants automatically
    normalized = unicodedata.normalize('NFKC', text)

    # Step 2: Apply confusables map for remaining lookalikes
    result: list[str] = []
    for char in normalized:
        # Replace confusable with Latin equivalent, or keep original
        result.append(CONFUSABLES.get(char, char))

    return ''.join(result)


def is_mixed_script(text: str, *, ignore_common: bool = True) -> bool:
    """Detect if text mixes incompatible scripts (e.g., Latin + Cyrillic).

    Args:
        text: Input string to analyze
        ignore_common: If True, ignore Common/Inherited scripts (numbers,
                      punctuation, emoji). Default: True

    Returns:
        True if text contains mixed scripts within non-whitespace runs

    Examples:
        >>> is_mixed_script("hello")  # Pure Latin
        False
        >>> is_mixed_script("привет")  # Pure Cyrillic
        False
        >>> is_mixed_script("helloпривет")  # Mixed Latin+Cyrillic
        True
        >>> is_mixed_script("hello123")  # Numbers are Common script
        False
        >>> is_mixed_script("hello мир")  # Different words, different scripts
        False
    """
    if not text:
        return False

    # Fast path: ASCII is always purely Latin (or Common).
    # If we ignore Common, then ASCII text is never mixed-script.
    if ignore_common and text.isascii():
        return False

    # Split text into words (whitespace-separated tokens)
    words = text.split()

    for word in words:
        scripts_in_word: set[str] = set()

        for char in word:
            script = _get_script_name(char)

            # Ignore Common/Inherited scripts if configured
            if ignore_common and script in ('Common', 'Inherited', 'Unknown'):
                continue

            scripts_in_word.add(script)

        # If a single word has multiple scripts, it's mixed
        if len(scripts_in_word) > 1:
            return True

    return False


def get_script_blocks(text: str) -> list[tuple[str, int, int]]:
    """Identify script blocks in text.

    Args:
        text: Input string to analyze

    Returns:
        List of (script_name, start_pos, end_pos) tuples

    Examples:
        >>> get_script_blocks("hello")
        [('Latin', 0, 5)]
        >>> get_script_blocks("helloпривет")
        [('Latin', 0, 5), ('Cyrillic', 5, 11)]
        >>> blocks = get_script_blocks("test123")
        >>> len(blocks)
        2
        >>> blocks[0][0]  # First block is Latin
        'Latin'
    """
    if not text:
        return []

    blocks: list[tuple[str, int, int]] = []
    current_script = _get_script_name(text[0])
    start_pos = 0

    for pos, char in enumerate(text[1:], start=1):
        script = _get_script_name(char)

        # Script changed - record previous block
        if script != current_script:
            blocks.append((current_script, start_pos, pos))
            current_script = script
            start_pos = pos

    # Add final block
    blocks.append((current_script, start_pos, len(text)))

    return blocks


def detect_confusables(
    text: str, target_script: str = "Latin"
) -> list[tuple[int, str, str]]:
    """Find characters that look like target script but aren't.

    Args:
        text: Input string to analyze
        target_script: Script to check against (default: "Latin")

    Returns:
        List of (position, character, confusable_with) tuples

    Examples:
        >>> detect_confusables("pаypal")  # Cyrillic 'а' looks like Latin 'a'
        [(1, 'а', 'a')]
        >>> detect_confusables("hello")  # All Latin
        []
        >>> result = detect_confusables("gοοgle")  # Greek 'ο'
        >>> len(result)
        2
        >>> result[0][2]  # Confusable with
        'o'
    """
    # Fast path: ASCII text is already Latin/Common, so it cannot contain
    # characters from other scripts that mimic Latin.
    if text.isascii() and target_script == "Latin":
        return []

    result: list[tuple[int, str, str]] = []

    for pos, char in enumerate(text):
        # Check if character is a known confusable
        if char in CONFUSABLES:
            latin_equivalent = CONFUSABLES[char]
            # Character looks like target script but isn't
            script = _get_script_name(char)
            if script != target_script:
                result.append((pos, char, latin_equivalent))

    return result


# Internal helper: Get script name for a character
@lru_cache(maxsize=4096)
def _get_script_name(char: str) -> str:
    """Get Unicode script name for character.

    Uses binary search over generated Unicode data tables.

    Args:
        char: Single character

    Returns:
        Script name (e.g., "Latin", "Cyrillic", "Greek", "Common")
    """
    if len(char) != 1:
        return "Unknown"

    codepoint = ord(char)

    # Binary search to find the script range
    # SCRIPT_RANGES is a sorted list of (start_cp, script_name)
    # bisect_right returns the insertion point to maintain order
    # index-1 gives the range that starts <= codepoint
    idx = bisect.bisect_right(SCRIPT_RANGES, (codepoint, 'zzzzzz'))

    if idx == 0:
        return "Unknown"

    start_cp, script = SCRIPT_RANGES[idx - 1]

    # Note: Our generator fills gaps with "Unknown", so this covers
    # the case where codepoint is in a gap (implicit or explicit)

    if script in ('Hiragana', 'Katakana', 'Han', 'Hangul'):
        return 'CJK'

    if script == "Unknown":
        # Fallback to category heuristics for Common/Inherited if unknown script
        # This handles characters not yet in our table or special categories
        category = unicodedata.category(char)
        if category.startswith('N') or category.startswith('P') or \
           category.startswith('S') or category.startswith('Z'):
            return "Common"
        if category.startswith('M'):
            return "Inherited"

    return script

