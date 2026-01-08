"""Tests for segments module."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from indium import segments


class TestSafeTruncate:
    """Tests for safe_truncate() function."""

    def test_truncate_simple_text(self):
        """Test truncating simple ASCII text."""
        text = "hello world"
        result = segments.safe_truncate(text, 5)
        assert result == "hello"

    def test_truncate_with_combining_mark(self):
        """Test truncating text with combining marks."""
        text = "café"  # é = e + combining acute
        result = segments.safe_truncate(text, 3)
        # Should truncate to "caf", not breaking the é
        assert result == "caf"

    def test_truncate_emoji_sequence(self):
        """Test truncating emoji sequence."""
        text = "👨\u200D👩\u200D👧test"  # Family emoji + text
        result = segments.safe_truncate(text, 2)
        # Should keep family emoji as one unit
        assert "\u200D" in result  # ZWJ should be preserved
        assert result.endswith("t")

    def test_truncate_emoji_with_skin_tone(self):
        """Test truncating emoji with skin tone modifier."""
        text = "hello👋🏽world"  # Waving hand with skin tone
        result = segments.safe_truncate(text, 6)
        # Should preserve emoji with skin tone
        assert "👋🏽" in result

    def test_truncate_zero_graphemes(self):
        """Test truncating to zero graphemes."""
        text = "hello"
        result = segments.safe_truncate(text, 0)
        assert result == ""

    def test_truncate_negative_raises_error(self):
        """Test that negative max_graphemes raises error."""
        with pytest.raises(ValueError, match="non-negative"):
            segments.safe_truncate("test", -1)

    def test_truncate_exceeds_length(self):
        """Test truncating beyond text length."""
        text = "hi"
        result = segments.safe_truncate(text, 10)
        assert result == "hi"

    def test_truncate_empty_string(self):
        """Test truncating empty string."""
        assert segments.safe_truncate("", 5) == ""

    @given(st.text(), st.integers(min_value=0, max_value=100))
    def test_truncate_result_length(self, text, max_graphemes):
        """Property: truncated text has at most max_graphemes."""
        result = segments.safe_truncate(text, max_graphemes)
        assert segments.count_graphemes(result) <= max_graphemes


class TestCountGraphemes:
    """Tests for count_graphemes() function."""

    def test_count_simple_text(self):
        """Test counting simple ASCII text."""
        text = "hello"
        assert segments.count_graphemes(text) == 5

    def test_count_with_combining_mark(self):
        """Test counting with combining marks."""
        text = "café"  # é = e + combining acute accent
        # café should be 4 graphemes (c, a, f, é)
        assert segments.count_graphemes(text) == 4

    def test_count_emoji_sequence(self):
        """Test counting emoji sequence."""
        text = "👨\u200D👩\u200D👧"  # Family emoji
        # Family emoji is one grapheme cluster
        assert segments.count_graphemes(text) == 1

    def test_count_emoji_with_skin_tone(self):
        """Test counting emoji with skin tone."""
        text = "👋🏽"  # Waving hand + skin tone modifier
        # Should count as one grapheme
        assert segments.count_graphemes(text) == 1

    def test_count_flag_emoji(self):
        """Test counting flag emoji (regional indicators)."""
        text = "🇺🇸"  # US flag (two regional indicators)
        # Should count as one grapheme
        assert segments.count_graphemes(text) == 1

    def test_count_empty_string(self):
        """Test counting empty string."""
        assert segments.count_graphemes("") == 0

    def test_count_mixed_content(self):
        """Test counting mixed content."""
        text = "hello👋🏽"  # ASCII + emoji with skin tone
        # h, e, l, l, o, 👋🏽 = 6 graphemes
        assert segments.count_graphemes(text) == 6


class TestGraphemeSlice:
    """Tests for grapheme_slice() function."""

    def test_slice_simple_text(self):
        """Test slicing simple text."""
        text = "hello"
        result = segments.grapheme_slice(text, 1, 4)
        assert result == "ell"

    def test_slice_with_combining_marks(self):
        """Test slicing with combining marks."""
        text = "café"
        result = segments.grapheme_slice(text, 0, 3)
        assert result == "caf"

    def test_slice_emoji_sequence(self):
        """Test slicing emoji sequence."""
        text = "👨\u200D👩\u200D👧test"  # Family emoji + text
        result = segments.grapheme_slice(text, 1, 3)
        # Should get "te" (2nd and 3rd graphemes)
        assert result == "te"

    def test_slice_no_end(self):
        """Test slicing without end parameter."""
        text = "hello"
        result = segments.grapheme_slice(text, 2)
        assert result == "llo"

    def test_slice_negative_start_raises_error(self):
        """Test that negative start raises error."""
        with pytest.raises(ValueError, match="non-negative"):
            segments.grapheme_slice("test", -1, 2)

    def test_slice_end_before_start_raises_error(self):
        """Test that end < start raises error."""
        with pytest.raises(ValueError, match=">="):
            segments.grapheme_slice("test", 3, 1)

    def test_slice_beyond_text(self):
        """Test slicing beyond text length."""
        text = "hi"
        result = segments.grapheme_slice(text, 5, 10)
        assert result == ""

    def test_slice_empty_string(self):
        """Test slicing empty string."""
        result = segments.grapheme_slice("", 0, 5)
        assert result == ""


class TestIterGraphemes:
    """Tests for iter_graphemes() function."""

    def test_iter_simple_text(self):
        """Test iterating simple text."""
        text = "hello"
        result = list(segments.iter_graphemes(text))
        assert result == ["h", "e", "l", "l", "o"]

    def test_iter_with_combining_marks(self):
        """Test iterating with combining marks."""
        text = "café"
        result = list(segments.iter_graphemes(text))
        assert len(result) == 4
        # Last grapheme should be "é" (e + combining acute)
        assert result == ["c", "a", "f", "é"]

    def test_iter_emoji_sequence(self):
        """Test iterating emoji sequence."""
        text = "a👋🏽b"  # ASCII + emoji with skin tone + ASCII
        result = list(segments.iter_graphemes(text))
        assert len(result) == 3
        assert result[0] == "a"
        assert "👋" in result[1]  # Middle is emoji with skin tone
        assert result[2] == "b"

    def test_iter_empty_string(self):
        """Test iterating empty string."""
        result = list(segments.iter_graphemes(""))
        assert result == []

    def test_iter_family_emoji(self):
        """Test iterating family emoji."""
        text = "👨\u200D👩\u200D👧"
        result = list(segments.iter_graphemes(text))
        # Family emoji should be one grapheme
        assert len(result) == 1
        assert "\u200D" in result[0]  # ZWJ preserved


class TestGraphemeBoundaries:
    """Tests for grapheme boundary detection helpers."""

    def test_is_grapheme_boundary_start(self):
        """Test boundary at start of string."""
        text = "hello"
        assert segments._is_grapheme_boundary(text, 0)

    def test_is_grapheme_boundary_end(self):
        """Test boundary at end of string."""
        text = "hello"
        assert segments._is_grapheme_boundary(text, len(text))

    def test_not_boundary_combining_mark(self):
        """Test not a boundary before combining mark."""
        text = "e\u0301"  # e + combining acute
        # Position 1 (before combining mark) is NOT a boundary
        assert not segments._is_grapheme_boundary(text, 1)

    def test_not_boundary_zwj(self):
        """Test not a boundary within ZWJ sequence (Emoji)."""
        text = "👨\u200D👩"  # Man + ZWJ + Woman
        # Position after ZWJ (index 2) is not a boundary
        # Man (0), ZWJ (1), Woman (2)
        # Note: Man is 1 char? No, Man is \U0001F468 (1 char wide in Python 3, usually).
        # Let's verify indices.
        # len("👨") is 1. len(ZWJ) is 1.
        # Indices: 0 (Man), 1 (ZWJ), 2 (Woman)
        # Boundary at 2 means between ZWJ and Woman.
        assert not segments._is_grapheme_boundary(text, 2)

    # _is_regional_indicator removed in v1.0 refactor


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_malformed_unicode_handled(self):
        """Test that malformed unicode is handled gracefully."""
        # Note: Python strings are always valid Unicode
        # This test verifies we don't crash on unusual combinations
        text = "\u0301\u0302\u0303"  # Multiple combining marks
        result = segments.count_graphemes(text)
        assert result >= 0  # Should not crash

    def test_very_long_grapheme_cluster(self):
        """Test handling very long grapheme cluster."""
        # Create a base character with many combining marks
        text = "e" + "\u0301" * 10  # e + 10 combining acutes
        result = segments.count_graphemes(text)
        # Should count as one grapheme
        assert result == 1

    def test_mixed_emoji_and_text(self):
        """Test mixed emoji and text."""
        text = "hello👋world🌍test"
        graphemes = list(segments.iter_graphemes(text))
        # Should correctly separate text and emoji
        assert "h" in graphemes
        assert any("👋" in g for g in graphemes)
        assert any("🌍" in g for g in graphemes)
