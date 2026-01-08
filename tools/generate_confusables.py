#!/usr/bin/env python3
"""
Generate src/indium/_confusables.py from Unicode Consortium data.

Usage:
    python3 tools/generate_confusables.py [path/to/confusables.txt]

If path is not provided, tries to download from unicode.org.
"""

import datetime
import os
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Tuple

URL = "https://www.unicode.org/Public/security/15.1.0/confusables.txt"
# Output relative to this script: ../src/indium/_confusables.py
OUTPUT_FILE = Path(__file__).parent.parent / "src" / "indium" / "_confusables.py"

HEADER = f'''"""Confusable character mappings for homoglyph detection.

AUTO-GENERATED FILE - DO NOT EDIT MANUALLY.
Generated on {datetime.datetime.now().isoformat()}

Data Source: Unicode® Consortium (UTS #39 - Unicode Security Mechanisms)
Copyright © Unicode, Inc.
Unicode and the Unicode Logo are registered trademarks of Unicode, Inc.
License: Unicode License v3 (https://www.unicode.org/license.txt)

This module provides mappings from visually similar characters to their
canonical Latin equivalents, derived from Unicode confusables.txt.
"""

from typing import Final


'''

def parse_line(line: str) -> Tuple[str, str, str, str]:
    """Parse a line from confusables.txt.

    Returns: (source_char, target_char, type, comment)
    """
    # Format: 0430 ; 0061 ; MA # ...
    data, comment = line.split('#', 1)
    fields = [f.strip() for f in data.split(';')]

    if len(fields) < 3:
        return None

    source_hex = fields[0]
    target_hex = fields[1]
    mapping_type = fields[2]

    # Convert hex to characters
    # Source is always a single code point
    source_char = chr(int(source_hex, 16))

    # Target can be a sequence of code points
    target_char = "".join(chr(int(cp, 16)) for cp in target_hex.split())

    return source_char, target_char, mapping_type, comment.strip()

def generate(input_path: str):
    print(f"Reading from {input_path}...")

    mappings: Dict[str, Tuple[str, str]] = {}

    with open(input_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                result = parse_line(line)
                if not result:
                    continue

                source, target, kind, comment = result

                # Filter: strictly ensure target is Latin/Common (ASCII)
                # We only want to map "weird stuff" -> "normal stuff"
                if not target.isascii():
                    continue

                # Don't map ASCII to ASCII (e.g. 0 to O is confusable, but dangerous to map blindly)
                if source.isascii():
                    continue

                mappings[source] = (target, comment)

            except Exception as e:
                print(f"Skipping line: {line} ({e})")

    print(f"Found {len(mappings)} valid mappings.")

    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(HEADER)
        f.write("CONFUSABLES: Final[dict[str, str]] = {\n")

        # Sort by hex value for stability
        for source in sorted(mappings.keys()):
            target, comment = mappings[source]
            hex_val = f"U+{ord(source):04X}"

            # Escape chars for python string
            src_repr = repr(source)
            tgt_repr = repr(target)

            f.write(f"    {src_repr}: {tgt_repr},  # {hex_val} {comment}\n")

        f.write("}\n")

    print(f"Written to {OUTPUT_FILE}")

def main():
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        # Default fallback to checking local mock first, then download
        mock_path = "tools/data/confusables.txt"
        if os.path.exists(mock_path):
            input_path = mock_path
        else:
            print(f"Downloading from {URL}...")
            # Ensure directory exists
            download_dir = Path("tools/data")
            download_dir.mkdir(parents=True, exist_ok=True)
            
            input_path = str(download_dir / "confusables.txt")
            urllib.request.urlretrieve(URL, input_path)
            
    generate(input_path)
if __name__ == "__main__":
    main()