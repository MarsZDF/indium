"""Tests for spoofing module."""

from hypothesis import given
from hypothesis import strategies as st

from indium import spoofing


class TestSkeleton:
    """Tests for skeleton() function."""

    def test_skeleton_cyrillic_to_latin(self):
        """Test converting Cyrillic to Latin."""
        text = "pаypal"  # Cyrillic 'а'
        result = spoofing.skeleton(text)
        assert result == "paypal"

    def test_skeleton_greek_to_latin(self):
        """Test converting Greek to Latin."""
        text = "gοοgle"  # Greek 'ο' (omicron)
        result = spoofing.skeleton(text)
        assert result == "google"

    def test_skeleton_fullwidth_to_latin(self):
        """Test converting fullwidth to Latin."""
        text = "ｆａｃｅｂｏｏｋ"
        result = spoofing.skeleton(text)
        assert result == "facebook"

    def test_skeleton_mixed_confusables(self):
        """Test mixed confusable characters."""
        text = "pаypаl"  # Multiple Cyrillic 'а'
        result = spoofing.skeleton(text)
        assert result == "paypal"

    def test_skeleton_no_confusables(self):
        """Test text with no confusables."""
        text = "hello"
        result = spoofing.skeleton(text)
        assert result == "hello"

    def test_skeleton_empty_string(self):
        """Test empty string."""
        assert spoofing.skeleton("") == ""

    @given(st.text())
    def test_skeleton_idempotent(self, text):
        """Property: skeleton is idempotent."""
        result1 = spoofing.skeleton(text)
        result2 = spoofing.skeleton(result1)
        assert result1 == result2


class TestIsMixedScript:
    """Tests for is_mixed_script() function."""

    def test_pure_latin(self):
        """Test pure Latin text."""
        assert not spoofing.is_mixed_script("hello")

    def test_pure_cyrillic(self):
        """Test pure Cyrillic text."""
        assert not spoofing.is_mixed_script("привет")

    def test_mixed_latin_cyrillic(self):
        """Test mixed Latin and Cyrillic."""
        text = "helloпривет"
        assert spoofing.is_mixed_script(text)

    def test_mixed_separated_by_whitespace(self):
        """Test different scripts separated by whitespace."""
        text = "hello привет"  # Different words
        assert not spoofing.is_mixed_script(text)

    def test_with_numbers(self):
        """Test that numbers don't trigger mixed script."""
        text = "hello123"
        assert not spoofing.is_mixed_script(text)

    def test_with_punctuation(self):
        """Test that punctuation doesn't trigger mixed script."""
        text = "hello, world!"
        assert not spoofing.is_mixed_script(text)

    def test_empty_string(self):
        """Test empty string."""
        assert not spoofing.is_mixed_script("")

    def test_ignore_common_false(self):
        """Test with ignore_common=False."""
        text = "hello123"
        # With ignore_common=False, numbers are treated as separate script
        result = spoofing.is_mixed_script(text, ignore_common=False)
        # Latin letters + Common (numbers) = mixed
        assert result


class TestGetScriptBlocks:
    """Tests for get_script_blocks() function."""

    def test_single_script(self):
        """Test single script block."""
        text = "hello"
        result = spoofing.get_script_blocks(text)
        assert len(result) == 1
        assert result[0][0] == "Latin"
        assert result[0][1] == 0
        assert result[0][2] == 5

    def test_two_scripts(self):
        """Test two script blocks."""
        text = "helloпривет"
        result = spoofing.get_script_blocks(text)
        assert len(result) >= 2
        assert "Latin" in [block[0] for block in result]
        assert "Cyrillic" in [block[0] for block in result]

    def test_with_common_script(self):
        """Test with common script (numbers, punctuation)."""
        text = "test123"
        result = spoofing.get_script_blocks(text)
        # Should have Latin and Common blocks
        assert len(result) >= 1

    def test_empty_string(self):
        """Test empty string."""
        result = spoofing.get_script_blocks("")
        assert result == []


class TestDetectConfusables:
    """Tests for detect_confusables() function."""

    def test_detect_cyrillic_in_latin(self):
        """Test detecting Cyrillic confusables."""
        text = "pаypal"  # Cyrillic 'а' at position 1
        result = spoofing.detect_confusables(text)
        assert len(result) == 1
        assert result[0][0] == 1  # Position
        assert result[0][1] == "а"  # Cyrillic character
        assert result[0][2] == "a"  # Latin equivalent

    def test_detect_multiple_confusables(self):
        """Test detecting multiple confusables."""
        text = "pаypаl"  # Two Cyrillic 'а'
        result = spoofing.detect_confusables(text)
        assert len(result) == 2

    def test_no_confusables(self):
        """Test text with no confusables."""
        text = "hello"
        result = spoofing.detect_confusables(text)
        assert result == []

    def test_greek_confusables(self):
        """Test detecting Greek confusables."""
        text = "gοοgle"  # Greek 'ο' (omicron)
        result = spoofing.detect_confusables(text)
        assert len(result) == 2  # Two Greek 'ο'
        assert all(conf[2] == "o" for conf in result)

    def test_empty_string(self):
        """Test empty string."""
        result = spoofing.detect_confusables("")
        assert result == []


class TestGetScriptName:
    """Tests for _get_script_name() helper."""

    def test_latin_script(self):
        """Test Latin characters."""
        assert spoofing._get_script_name("a") == "Latin"
        assert spoofing._get_script_name("Z") == "Latin"

    def test_cyrillic_script(self):
        """Test Cyrillic characters."""
        assert spoofing._get_script_name("а") == "Cyrillic"
        assert spoofing._get_script_name("Я") == "Cyrillic"

    def test_greek_script(self):
        """Test Greek characters."""
        assert spoofing._get_script_name("α") == "Greek"
        assert spoofing._get_script_name("Ω") == "Greek"

    def test_common_script(self):
        """Test common characters (numbers, punctuation)."""
        assert spoofing._get_script_name("1") == "Common"
        assert spoofing._get_script_name(".") == "Common"
        assert spoofing._get_script_name(" ") == "Common"

    def test_inherited_script(self):
        """Test inherited script (combining marks)."""
        assert spoofing._get_script_name("\u0301") == "Inherited"  # Combining acute
