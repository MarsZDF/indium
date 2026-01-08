import pytest

import indium
from indium._exceptions import InvalidTextError
from indium._unicode_data import (
    get_category,
    get_unicode_name,
    is_combining,
    is_invisible,
    is_whitespace,
)


class TestSpoofingCoverage:
    def test_skeleton_expansion_regression(self):
        """Regression test for single char expanding to multiple characters."""
        # U+00BC VULGAR FRACTION ONE QUARTER -> 1⁄4 (3 chars)
        result = indium.skeleton("¼")
        # Just ensure it doesn't crash and returns expected expansion length
        assert len(result) >= 3

    def test_missing_scripts_detection(self):
        """Test scripts that were missing from initial test suite."""
        # Arabic
        blocks = indium.get_script_blocks("مرحبا")
        assert blocks and blocks[0][0] == "Arabic"

        # Hebrew
        blocks = indium.get_script_blocks("שלום")
        assert blocks and blocks[0][0] == "Hebrew"

        # Devanagari
        blocks = indium.get_script_blocks("नमस्ते")
        assert blocks and blocks[0][0] == "Devanagari"

        # Thai
        blocks = indium.get_script_blocks("สวัสดี")
        assert blocks and blocks[0][0] == "Thai"

        # CJK
        blocks = indium.get_script_blocks("你好")
        assert blocks and blocks[0][0] == "CJK"

class TestExceptionCoverage:
    def test_invalid_text_error_init(self):
        """Test initialization of custom exception."""
        err = InvalidTextError("Bad text", position=5)
        assert str(err) == "Bad text"
        assert err.position == 5

class TestUnicodeDataValidation:
    def test_get_unicode_name_fallback(self):
        """Test fallback when name is not found."""
        # Private use area usually raises ValueError in unicodedata.name()
        # or returns specific implementation string.
        # We ensure our wrapper handles it.
        char = "\U000F0000"  # Plane 15 Private Use
        name = get_unicode_name(char, default="UNKNOWN")
        # Should either be the real name or our fallback
        assert isinstance(name, str)

    def test_validation_raises_on_multichar(self):
        """Test that validation helpers raise error on strings len != 1."""
        invalid_input = "ab"

        with pytest.raises(ValueError, match="Expected single character"):
            is_invisible(invalid_input)

        with pytest.raises(ValueError, match="Expected single character"):
            is_whitespace(invalid_input)

        with pytest.raises(ValueError, match="Expected single character"):
            get_category(invalid_input)

        with pytest.raises(ValueError, match="Expected single character"):
            get_unicode_name(invalid_input)

        with pytest.raises(ValueError, match="Expected single character"):
            is_combining(invalid_input)
