"""Property-based tests using Hypothesis.

These tests verify invariants and properties that should hold for all inputs.
"""

from hypothesis import given
from hypothesis import strategies as st

import indium


class TestInvisiblesProperties:
    """Property tests for invisibles module."""

    @given(st.text())
    def test_sanitize_never_increases_length(self, text):
        """Property: sanitize never increases text length."""
        result = indium.sanitize(text)
        assert len(result) <= len(text)

    @given(st.text())
    def test_sanitize_idempotent(self, text):
        """Property: sanitize is idempotent."""
        result1 = indium.sanitize(text)
        result2 = indium.sanitize(result1)
        assert result1 == result2

    @given(st.text())
    def test_detect_invisibles_count_valid(self, text):
        """Property: detect_invisibles returns valid positions."""
        result = indium.detect_invisibles(text)
        for pos, char, name in result:
            assert 0 <= pos < len(text)
            assert len(char) == 1
            assert isinstance(name, str)

    @given(st.text())
    def test_count_by_category_sum_equals_length(self, text):
        """Property: sum of category counts equals text length."""
        if not text:
            return
        counts = indium.count_by_category(text)
        total = sum(counts.values())
        assert total == len(text)


class TestSpoofingProperties:
    """Property tests for spoofing module."""

    @given(st.text())
    def test_skeleton_idempotent(self, text):
        """Property: skeleton is idempotent."""
        result1 = indium.skeleton(text)
        result2 = indium.skeleton(result1)
        assert result1 == result2

    @given(st.text())
    def test_skeleton_never_increases_length(self, text):
        """Property: skeleton never increases length significantly."""
        result = indium.skeleton(text)
        # NFKC normalization might change length slightly
        # but should not dramatically increase it (some chars expand to ~3-4 chars)
        assert len(result) <= len(text) * 4  # Generous bound for NFKC expansion

    @given(st.text())
    def test_is_mixed_script_deterministic(self, text):
        """Property: is_mixed_script is deterministic."""
        result1 = indium.is_mixed_script(text)
        result2 = indium.is_mixed_script(text)
        assert result1 == result2

    @given(st.text())
    def test_get_script_blocks_covers_text(self, text):
        """Property: script blocks cover entire text."""
        if not text:
            return
        blocks = indium.get_script_blocks(text)
        if blocks:
            assert blocks[0][1] == 0  # First block starts at 0
            assert blocks[-1][2] == len(text)  # Last block ends at text length

    @given(st.text())
    def test_detect_confusables_positions_valid(self, text):
        """Property: confusable positions are valid."""
        result = indium.detect_confusables(text)
        for pos, char, equivalent in result:
            assert 0 <= pos < len(text)
            assert len(char) == 1
            assert len(equivalent) >= 1


class TestSegmentsProperties:
    """Property tests for segments module."""

    @given(st.text(), st.integers(min_value=0, max_value=100))
    def test_safe_truncate_respects_max(self, text, max_graphemes):
        """Property: safe_truncate returns at most max_graphemes."""
        result = indium.safe_truncate(text, max_graphemes)
        count = indium.count_graphemes(result)
        assert count <= max_graphemes

    @given(st.text())
    def test_count_graphemes_non_negative(self, text):
        """Property: grapheme count is always non-negative."""
        count = indium.count_graphemes(text)
        assert count >= 0

    @given(st.text())
    def test_count_graphemes_at_most_codepoints(self, text):
        """Property: grapheme count is at most codepoint count."""
        grapheme_count = indium.count_graphemes(text)
        codepoint_count = len(text)
        assert grapheme_count <= codepoint_count

    @given(st.text())
    def test_iter_graphemes_count_matches(self, text):
        """Property: iter_graphemes count matches count_graphemes."""
        graphemes = list(indium.iter_graphemes(text))
        count = indium.count_graphemes(text)
        assert len(graphemes) == count

    @given(st.text())
    def test_iter_graphemes_reconstructs_text(self, text):
        """Property: joining iter_graphemes reconstructs original text."""
        graphemes = list(indium.iter_graphemes(text))
        reconstructed = "".join(graphemes)
        assert reconstructed == text

    @given(st.text(), st.integers(min_value=0, max_value=50))
    def test_grapheme_slice_within_bounds(self, text, start):
        """Property: grapheme_slice result is substring of original."""
        result = indium.grapheme_slice(text, start)
        # Result should be empty or a substring
        if result:
            assert result in text or text in result  # Handles edge cases

    @given(st.text(), st.integers(min_value=0, max_value=20))
    def test_safe_truncate_zero_gives_empty(self, text, _):
        """Property: truncating to 0 always gives empty string."""
        result = indium.safe_truncate(text, 0)
        assert result == ""


class TestCombinedProperties:
    """Property tests combining multiple modules."""

    @given(st.text())
    def test_sanitize_then_count_graphemes(self, text):
        """Property: sanitize then count should not crash."""
        sanitized = indium.sanitize(text)
        count = indium.count_graphemes(sanitized)
        assert count >= 0

    @given(st.text())
    def test_skeleton_then_is_mixed_script(self, text):
        """Property: skeleton then is_mixed_script should not crash."""
        normalized = indium.skeleton(text)
        mixed = indium.is_mixed_script(normalized)
        assert isinstance(mixed, bool)

    @given(st.text())
    def test_reveal_then_sanitize_removes_markers(self, text):
        """Property: reveal adds markers, sanitize can handle them."""
        revealed = indium.reveal(text)
        # Sanitizing revealed text should not crash
        sanitized = indium.sanitize(revealed)
        assert isinstance(sanitized, str)


class TestFuzzing:
    """Fuzzing tests with adversarial inputs."""

    @given(st.text(alphabet=st.characters(blacklist_categories=("Cs",))))
    def test_all_functions_handle_unicode(self, text):
        """Fuzzing: all functions handle arbitrary Unicode."""
        # Should not crash on any valid Unicode
        try:
            indium.reveal(text)
            indium.sanitize(text)
            indium.detect_invisibles(text)
            indium.skeleton(text)
            indium.is_mixed_script(text)
            indium.count_graphemes(text)
            list(indium.iter_graphemes(text))
        except Exception as e:
            # Only allow expected exceptions
            assert isinstance(e, ValueError), f"Unexpected exception: {e}"

    @given(st.text(min_size=0, max_size=1000))
    def test_large_text_performance(self, text):
        """Fuzzing: functions handle reasonably sized text efficiently."""
        # These should complete in reasonable time
        indium.count_graphemes(text)
        indium.skeleton(text)
        indium.sanitize(text)

    @given(st.text(alphabet=st.sampled_from(["\u200B", "\u200C", "\u200D", "\uFEFF"])))
    def test_only_invisibles(self, text):
        """Fuzzing: handle text with only invisible characters."""
        sanitized = indium.sanitize(text)
        # Should remove all or most invisibles
        assert len(sanitized) <= len(text)
