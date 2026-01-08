#!/usr/bin/env python3
"""
Generate src/indium/_scripts_data.py from Unicode Consortium data.

Usage:
    python3 tools/generate_scripts.py [path/to/Scripts.txt]

Generates a bisect-able table of script ranges.
"""

import datetime
import os
import sys
import urllib.request
from pathlib import Path
from typing import List, Tuple

URL = "https://www.unicode.org/Public/15.1.0/ucd/Scripts.txt"
# Output relative to this script: ../src/indium/_scripts_data.py
OUTPUT_FILE = Path(__file__).parent.parent / "src" / "indium" / "_scripts_data.py"

HEADER = f'''"""Unicode Script property data.

AUTO-GENERATED FILE - DO NOT EDIT MANUALLY.
Generated on {datetime.datetime.now().isoformat()}

Data Source: Unicode® Consortium (Scripts.txt)
Copyright © Unicode, Inc.
Unicode and the Unicode Logo are registered trademarks of Unicode, Inc.
License: Unicode License v3 (https://www.unicode.org/license.txt)

This module provides an efficient lookup table for determining the Script
property of a Unicode code point using binary search.
"""

from typing import Final


'''

def parse_line(line: str) -> Tuple[int, int, str]:
    """Parse a line from Scripts.txt.
    Returns: (start_cp, end_cp, script_name)
    """
    # Format: 0000..001F    ; Common # Cc  [32] <control-0000>..<control-001F>
    if '#' in line:
        data, _ = line.split('#', 1)
    else:
        data = line

    parts = [p.strip() for p in data.split(';')]
    if len(parts) < 2:
        return None

    range_part = parts[0]
    script_name = parts[1]

    if '..' in range_part:
        start_hex, end_hex = range_part.split('..')
        start = int(start_hex, 16)
        end = int(end_hex, 16)
    else:
        start = int(range_part, 16)
        end = start

    return start, end, script_name

def generate(input_path: str):
    print(f"Reading from {input_path}...")

    ranges: List[Tuple[int, int, str]] = []

    with open(input_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                result = parse_line(line)
                if result:
                    ranges.append(result)
            except Exception as e:
                print(f"Skipping line: {line} ({e})")

    # Sort by start position
    ranges.sort()

    if not ranges:
        print("No data found!")
        return

    # Algorithm: We want a flat list of (start_codepoint, script_name)
    # for use with bisect_right.

    final_table: List[Tuple[int, str]] = []

    current_pos = 0
    current_script = "Unknown"

    for start, end, script in ranges:
        # If there is a gap, fill it with Unknown (Zzzz)
        if start > current_pos and current_script != "Unknown":
            final_table.append((current_pos, "Unknown"))
            current_script = "Unknown"

        # Start of new range
        if script != current_script:
            # Avoid duplicate start keys if gap was 0 size
            if final_table and final_table[-1][0] == start:
                final_table.pop()

            final_table.append((start, script))
            current_script = script

        # The range goes until `end`.
        # The next range starts at `end + 1`.
        current_pos = end + 1

    # Add final sentinel? Not needed if we handle index out of bounds.

    print(f"Generated {len(final_table)} breakdown points from {len(ranges)} ranges.")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(HEADER)
        f.write("\n")
        f.write("# Sorted list of (start_codepoint, script_name)\n")
        f.write("# Use bisect.bisect_right to find the index\n")
        f.write("SCRIPT_RANGES: Final[tuple[tuple[int, str], ...]] = (\n")

        for start, script in final_table:
            f.write(f"    ({start}, '{script}'),\n")

        f.write(")\n")

    print(f"Written to {OUTPUT_FILE}")

def main():
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        mock_path = "tools/data/Scripts.txt"
        if os.path.exists(mock_path):
            input_path = mock_path
        else:
            print(f"Downloading from {URL}...")
            # Ensure directory exists
            download_dir = Path("tools/data")
            download_dir.mkdir(parents=True, exist_ok=True)
            
            input_path = str(download_dir / "Scripts.txt")
            urllib.request.urlretrieve(URL, input_path)

    generate(input_path)

if __name__ == "__main__":
    main()
