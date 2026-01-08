"""Full UAX #29 compliance suite.

Parses GraphemeBreakTest.txt and validates every test case.
"""

import os
from pathlib import Path

import pytest

import indium
from indium import segments

TEST_FILE = Path(__file__).parent.parent / "tools" / "data" / "GraphemeBreakTest.txt"

def parse_test_file(path: Path):
    """Parse the official test file."""
    if not path.exists():
        return []

    cases = []
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.split("#")[0].strip()
            if not line:
                continue

            # Format: ÷ 0020 × 0020 ÷
            parts = line.split()
            codepoints = []
            breaks = [] # Indices where breaks occur

            current_index = 0
            # Always starts with ÷

            for part in parts:
                if part == "÷":
                    breaks.append(current_index)
                elif part == "×":
                    pass
                else:
                    # Codepoint hex
                    cp = int(part, 16)
                    codepoints.append(cp)
                    current_index += 1

            # Construct expected strings
            expected_graphemes = []

            # breaks indices are relative to codepoint boundaries
            # breaks[0] is 0 (start)
            # breaks[-1] is len (end)

            # Reconstruct clusters
            full_text = "".join(chr(cp) for cp in codepoints)

            last_break = 0
            for b in breaks[1:]: # Skip first break at 0
                # b is the index in codepoints list
                # But wait, Python strings are unicode. slicing by codepoint index matches.
                # Assuming narrow build? No, Python 3 strings are unicode arrays conceptually.
                # But surrogates? on wide build (macOS/Linux usually), len(chr(0x10000)) == 1.
                # On Windows? We assume standard Python 3 behavior.

                # Wait, breaks are defined by codepoint count.
                # chr(cp) might return a string of length 1 or 2 (surrogates).
                # indium handles strings.
                # We need to slice the *codepoints list* to get the cluster, then join.

                cluster_cps = codepoints[last_break:b]
                cluster_str = "".join(chr(cp) for cp in cluster_cps)
                expected_graphemes.append(cluster_str)
                last_break = b

            cases.append((line_num, full_text, expected_graphemes))

    return cases

ALL_CASES = parse_test_file(TEST_FILE)

@pytest.mark.skipif(not TEST_FILE.exists(), reason="GraphemeBreakTest.txt not found (run tools/generate_grapheme_data.py)")
@pytest.mark.parametrize("line_num, text, expected", ALL_CASES)
def test_official_compliance(line_num, text, expected):
    """Run an official UAX #29 test case."""
    actual = list(segments.iter_graphemes(text))
    assert actual == expected, f"Line {line_num}: Expected {expected}, got {actual}"
