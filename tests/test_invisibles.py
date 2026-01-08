"""Tests for invisibles module."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from indium import invisibles


class TestReveal:
    """Tests for reveal() function."""

    def test_reveal_zero_width_space(self):
        """Test revealing zero-width space."""
        text = "hello\u200Bworld"
        result = invisibles.reveal(text)
        assert result == "hello<U+200B>world"

    def test_reveal_multiple_invisibles(self):
        """Test revealing multiple invisible characters."""
        text = "a\u200B\u200C\u200Db"  # ZWSP, ZWNJ, ZWJ
        result = invisibles.reveal(text)
        assert "<U+200B>" in result
        assert "<U+200C>" in result
        assert "<U+200D>" in result

    def test_reveal_format_unicode(self):
        """Test unicode format."""
        text = "test\u200B"
        result = invisibles.reveal(text, format="unicode")
        assert result == "test<U+200B>"

    def test_reveal_format_hex(self):
        """Test hex format."""
        text = "test\u200B"
        result = invisibles.reveal(text, format="hex")
        assert result == "test\\u200b"

    def test_reveal_format_name(self):
        """Test name format."""
        text = "test\u200B"
        result = invisibles.reveal(text, format="name")
        assert result == "test<ZERO WIDTH SPACE>"

    def test_reveal_invalid_format(self):
        """Test invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid format"):
            invisibles.reveal("test", format="invalid")

    def test_reveal_whitespace_substitute(self):
        """Test whitespace substitution."""
        text = "hello world"
        result = invisibles.reveal(text, substitute="·")
        assert result == "hello·world"

    def test_reveal_empty_string(self):
        """Test empty string."""
        assert invisibles.reveal("") == ""

    def test_reveal_no_invisibles(self):
        """Test text with no invisibles."""
        text = "plain text"
        result = invisibles.reveal(text)
        assert "plain" in result
        assert "text" in result


class TestSanitize:
    """Tests for sanitize() function."""

    def test_sanitize_zero_width_space(self):
        """Test removing zero-width space."""
        text = "hello\u200Bworld"
        result = invisibles.sanitize(text)
        assert result == "helloworld"

    def test_sanitize_preserves_regular_whitespace(self):
        """Test that regular spaces are preserved."""
        text = "hello world"
        result = invisibles.sanitize(text)
        assert result == "hello world"

    def test_sanitize_preserves_newlines(self):
        """Test that newlines are preserved."""
        text = "line1\nline2"
        result = invisibles.sanitize(text)
        assert result == "line1\nline2"

    def test_sanitize_strict_schema(self):
        """Test strict schema removes all invisibles."""
        text = "test\u200B\u200D"  # ZWSP and ZWJ
        result = invisibles.sanitize(text, schema="strict")
        assert result == "test"

    def test_sanitize_permissive_schema(self):
        """Test permissive schema keeps ZWJ."""
        text = "👨\u200D👩"  # Family emoji with ZWJ
        result = invisibles.sanitize(text, schema="permissive")
        assert "\u200D" in result

    def test_sanitize_preserve_zwj_override(self):
        """Test preserve_zwj overrides schema."""
        text = "👨\u200D👩"
        result = invisibles.sanitize(text, schema="strict", preserve_zwj=True)
        assert "\u200D" in result

    def test_sanitize_invalid_schema(self):
        """Test invalid schema raises error."""
        with pytest.raises(ValueError, match="Invalid schema"):
            invisibles.sanitize("test", schema="invalid")

    def test_sanitize_empty_string(self):
        """Test empty string."""
        assert invisibles.sanitize("") == ""

    @given(st.text())
    def test_sanitize_never_increases_length(self, text):
        """Property: sanitize never increases text length."""
        result = invisibles.sanitize(text)
        assert len(result) <= len(text)


class TestDetectInvisibles:
    """Tests for detect_invisibles() function."""

    def test_detect_single_invisible(self):
        """Test detecting single invisible character."""
        text = "hello\u200Bworld"
        result = invisibles.detect_invisibles(text)
        assert len(result) == 1
        assert result[0][0] == 5  # Position
        assert result[0][1] == "\u200B"  # Character
        assert "ZERO WIDTH SPACE" in result[0][2]  # Name

    def test_detect_multiple_invisibles(self):
        """Test detecting multiple invisibles."""
        text = "a\u200Bb\u200Cc"
        result = invisibles.detect_invisibles(text)
        assert len(result) == 2
        assert result[0][0] == 1
        assert result[1][0] == 3

    def test_detect_no_invisibles(self):
        """Test text with no invisibles."""
        text = "plain text"
        result = invisibles.detect_invisibles(text)
        assert result == []

    def test_detect_ignores_regular_whitespace(self):
        """Test that regular spaces are not detected."""
        text = "hello world"
        result = invisibles.detect_invisibles(text)
        assert result == []

    def test_detect_empty_string(self):
        """Test empty string."""
        result = invisibles.detect_invisibles("")
        assert result == []


class TestCountByCategory:
    """Tests for count_by_category() function."""

    def test_count_lowercase_letters(self):
        """Test counting lowercase letters."""
        text = "hello"
        result = invisibles.count_by_category(text)
        assert result.get("Ll", 0) == 5  # Lowercase letters

    def test_count_mixed_text(self):
        """Test counting mixed text."""
        text = "Hello World!"
        result = invisibles.count_by_category(text)
        assert result.get("Lu", 0) == 2  # Uppercase
        assert result.get("Ll", 0) == 8  # Lowercase
        assert result.get("Zs", 0) == 1  # Space separator
        assert result.get("Po", 0) == 1  # Punctuation

    def test_count_invisibles(self):
        """Test counting invisible characters."""
        text = "test\u200B"
        result = invisibles.count_by_category(text)
        assert result.get("Cf", 0) == 1  # Format category

    def test_count_empty_string(self):
        """Test empty string."""
        result = invisibles.count_by_category("")
        assert result == {}
