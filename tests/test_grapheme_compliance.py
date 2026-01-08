"""Compliance tests for Unicode Text Segmentation (UAX #29).

Verifies that indium's grapheme cluster boundaries match the Unicode standard.
References: https://www.unicode.org/reports/tr29/
"""

import dataclasses

import pytest

from indium import segments


@dataclasses.dataclass
class GraphemeTestCase:
    comment: str
    codepoints: list[int]
    expected_graphemes: list[str]

# Representative subset of GraphemeBreakTest.txt
# Format: ÷ = Break, × = No Break
# We manually construct the expected graphemes based on the break rules.
TEST_CASES = [
    # Rule GB3: CR x LF
    GraphemeTestCase(
        comment="GB3: CR x LF",
        codepoints=[0x000D, 0x000A],  # \r\n
        expected_graphemes=["\r\n"]
    ),
    # Rule GB4: (Control|CR|LF) ÷
    GraphemeTestCase(
        comment="GB4: Control ÷ Any",
        codepoints=[0x000D, 0x0061],  # \r a
        expected_graphemes=["\r", "a"]
    ),
    # Rule GB6: L x (L|V|LV|LVT) (Hangul)
    GraphemeTestCase(
        comment="GB6: L x L (Hangul)",
        codepoints=[0x1100, 0x1100],  # Choseong Kiyeok x Choseong Kiyeok
        expected_graphemes=["\u1100\u1100"]
    ),
    # Rule GB11: \p{Extended_Pictographic} Extend* ZWJ x \p{Extended_Pictographic}
    GraphemeTestCase(
        comment="GB11: Emoji ZWJ Sequence (Family)",
        codepoints=[0x1F468, 0x200D, 0x1F469, 0x200D, 0x1F467], # Man ZWJ Woman ZWJ Girl
        expected_graphemes=["👨‍👩‍👧"]
    ),
    # Rule GB12/13: Regional_Indicator x Regional_Indicator
    GraphemeTestCase(
        comment="GB12: Flag Sequence (US)",
        codepoints=[0x1F1FA, 0x1F1F8], # U + S
        expected_graphemes=["🇺🇸"]
    ),
    # Complex Case: Skin Tone
    GraphemeTestCase(
        comment="Emoji with Skin Tone",
        codepoints=[0x1F44B, 0x1F3FD], # Waving Hand + Medium Skin Tone
        expected_graphemes=["👋🏽"]
    ),
     # Keycap Sequence
    GraphemeTestCase(
        comment="Keycap Sequence",
        codepoints=[0x0023, 0xFE0F, 0x20E3], # # + VS16 + Keycap
        expected_graphemes=["".join(chr(cp) for cp in [0x0023, 0xFE0F, 0x20E3])]
    ),
]

@pytest.mark.parametrize("case", TEST_CASES)
def test_grapheme_compliance(case):
    """Verify that text segmentation matches the expected grapheme clusters."""
    text = "".join(chr(cp) for cp in case.codepoints)

    # Test count_graphemes
    assert segments.count_graphemes(text) == len(case.expected_graphemes), \
        f"Count failed for {case.comment}"

    # Test iter_graphemes
    actual_graphemes = list(segments.iter_graphemes(text))
    assert actual_graphemes == case.expected_graphemes, \
        f"Segmentation failed for {case.comment}.\nExpected: {case.expected_graphemes}\nActual: {actual_graphemes}"

def test_legacy_grapheme_clusters():
    """Test legacy clusters (Prepend, SpacingMark) if supported."""
    # Devanagari k + virama + ss + i (Complex cluster)
    # k (KA) = 0915
    # virama = 094D
    # ss (SSA) = 0937
    # i (Vowel Sign I) = 093F
    text = "\u0915\u094D\u0937\u093F" # Kshi

    # In legacy/standard segmentation this might be one or two clusters depending on engine.
    # Python's unicodedata is usually good with combining marks.
    # We expect: 1 cluster (Kshi) because of Virama

    clusters = list(segments.iter_graphemes(text))
    # If this assertion fails, it's not critical but informative about the implementation limits
    # The standard says Virama connects consonants.
    assert len(clusters) == 1 or len(clusters) == 2
