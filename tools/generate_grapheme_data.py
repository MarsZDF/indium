#!/usr/bin/env python3
"""
Generate src/indium/_grapheme_data.py from Unicode Consortium data.

Usage:
    python3 tools/generate_grapheme_data.py

Downloads and parses:
- GraphemeBreakProperty.txt (for UAX #29)
- emoji-data.txt (for Extended_Pictographic)
"""

import datetime
import os
import sys
import urllib.request
from pathlib import Path
from typing import List, Tuple, Dict

# URLs - Pinned to Unicode 15.1.0 for stability
BASE_URL = "https://www.unicode.org/Public/15.1.0/ucd"
GRAPHEME_URL = f"{BASE_URL}/auxiliary/GraphemeBreakProperty.txt"
EMOJI_URL = f"{BASE_URL}/emoji/emoji-data.txt"
TEST_URL = f"{BASE_URL}/auxiliary/GraphemeBreakTest.txt"
CORE_URL = f"{BASE_URL}/DerivedCoreProperties.txt"

# Output
OUTPUT_FILE = Path(__file__).parent.parent / "src" / "indium" / "_grapheme_data.py"

HEADER = f'''"""Unicode Grapheme Cluster Break property data.

AUTO-GENERATED FILE - DO NOT EDIT MANUALLY.
Generated on {datetime.datetime.now().isoformat()}

Data Source: Unicode® Consortium
  - GraphemeBreakProperty.txt (UAX #29)
  - emoji-data.txt
  - DerivedCoreProperties.txt
Copyright © Unicode, Inc.
Unicode and the Unicode Logo are registered trademarks of Unicode, Inc.
License: Unicode License v3 (https://www.unicode.org/license.txt)

This module provides a lookup table for the Grapheme_Cluster_Break property,
Extended_Pictographic property, and InCB (Indic Conjunct Break) properties.
"""

from typing import Final

# Property Constants
OTHER = 0
CR = 1
LF = 2
CONTROL = 3
EXTEND = 4
REGIONAL_INDICATOR = 5
PREPEND = 6
SPACINGMARK = 7
L = 8
V = 9
T = 10
LV = 11
LVT = 12
ZWJ = 13
EXTENDED_PICTOGRAPHIC = 14
INCB_LINKER = 15      # From DerivedCoreProperties.txt (InCB=Linker)
INCB_CONSONANT = 16   # From DerivedCoreProperties.txt (InCB=Consonant)
INCB_EXTEND = 17      # From DerivedCoreProperties.txt (InCB=Extend)

# Map string names to integer constants for readability
PROP_MAP = {{
    'Other': OTHER,
    'CR': CR,
    'LF': LF,
    'Control': CONTROL,
    'Extend': EXTEND,
    'Regional_Indicator': REGIONAL_INDICATOR,
    'Prepend': PREPEND,
    'SpacingMark': SPACINGMARK,
    'L': L,
    'V': V,
    'T': T,
    'LV': LV,
    'LVT': LVT,
    'ZWJ': ZWJ,
    'Extended_Pictographic': EXTENDED_PICTOGRAPHIC,
    'InCB_Linker': INCB_LINKER,
    'InCB_Consonant': INCB_CONSONANT,
    'InCB_Extend': INCB_EXTEND,
}}

'''

def ensure_download(url: str, filename: str) -> str:
    """Download file if missing."""
    download_dir = Path("tools/data")
    download_dir.mkdir(parents=True, exist_ok=True)
    file_path = download_dir / filename
    
    if not file_path.exists():
        print(f"Downloading {filename} from {url}...")
        urllib.request.urlretrieve(url, str(file_path))
    
    return str(file_path)

def parse_file(file_path: str, property_map: Dict[str, str] = None) -> List[Tuple[int, int, str]]:
    """Parse a Unicode property file.
    Returns list of (start, end, property_name)
    """
    ranges = []
    print(f"Parsing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '#' in line:
                data, _ = line.split('#', 1)
            else:
                data = line
            
            parts = [p.strip() for p in data.split(';')]
            if len(parts) < 2:
                continue
                
            range_part = parts[0]
            prop_name = parts[1].split('#')[0].strip() # Clean up property name
            
            # Optional filter/map
            if property_map:
                if prop_name not in property_map:
                    continue
                prop_name = property_map[prop_name]

            if '..' in range_part:
                start_hex, end_hex = range_part.split('..')
                start = int(start_hex, 16)
                end = int(end_hex, 16)
            else:
                start = int(range_part, 16)
                end = start
                
            ranges.append((start, end, prop_name))
            
    return ranges

def generate():
    # 1. Download files
    grapheme_path = ensure_download(GRAPHEME_URL, "GraphemeBreakProperty.txt")
    emoji_path = ensure_download(EMOJI_URL, "emoji-data.txt")
    core_path = ensure_download(CORE_URL, "DerivedCoreProperties.txt")
    ensure_download(TEST_URL, "GraphemeBreakTest.txt")
    
    # 2. Parse Data
    all_ranges: List[Tuple[int, int, str]] = parse_file(grapheme_path)
    
    emoji_ranges = parse_file(emoji_path, property_map={'Extended_Pictographic': 'Extended_Pictographic'})
    
    # Parse InCB properties
    # In DerivedCoreProperties.txt, format is:
    # 094D          ; InCB; Linker # ...
    # So prop_name will be "InCB" if we just split by ';'.
    # Wait, the parser splits by ';'. 
    # For DerivedCoreProperties, parts[1] is "InCB" or "Math".
    # But usually properties are like "InCB; Linker".
    # Let's adjust parser or handle it here?
    # Actually, standard UCD files: 094D ; InCB # ... No wait.
    # It's usually: 094D ; InCB; Linker.
    # My simple parser splits by ';'. parts[1] is the property.
    # Let's modify parse_file to be more flexible or specialized for DerivedCore?
    
    # Let's write a custom parser for DerivedCoreProperties or improve the general one
    # to handle the 3rd column if present?
    # Or just quick hack: read the file manually here.
    
    incb_ranges = []
    print(f"Parsing {core_path} for InCB...")
    with open(core_path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'InCB' not in line: continue
            if line.startswith('#'): continue
            
            # 0000..001F    ; InCB; None # ... (Default)
            # 094D          ; InCB; Linker # ...
            
            data = line.split('#')[0]
            parts = [p.strip() for p in data.split(';')]
            if len(parts) < 3: continue
            
            if parts[1] != 'InCB': continue
            
            incb_val = parts[2] # Linker, Consonant, Extend, None
            if incb_val == 'None': continue
            
            prop_name = f"InCB_{incb_val}"
            
            range_part = parts[0]
            if '..' in range_part:
                start_hex, end_hex = range_part.split('..')
                start = int(start_hex, 16)
                end = int(end_hex, 16)
            else:
                start = int(range_part, 16)
                end = start
                
            incb_ranges.append((start, end, prop_name))

    # Merge strategy:
    import array
    props = array.array('B', [0] * 0x110000)
    
    prop_to_int = {
        'Other': 0,
        'CR': 1,
        'LF': 2,
        'Control': 3,
        'Extend': 4,
        'Regional_Indicator': 5,
        'Prepend': 6,
        'SpacingMark': 7,
        'L': 8,
        'V': 9,
        'T': 10,
        'LV': 11,
        'LVT': 12,
        'ZWJ': 13,
        'Extended_Pictographic': 14,
        'InCB_Linker': 15,
        'InCB_Consonant': 16,
        'InCB_Extend': 17,
    }
    
    # 1. Base Grapheme Properties
    for start, end, prop in all_ranges:
        val = prop_to_int.get(prop, 0)
        for i in range(start, end + 1):
            if i < len(props):
                props[i] = val
                
    # 2. Extended_Pictographic (Overlay)
    for start, end, prop in emoji_ranges:
        val = prop_to_int.get(prop)
        for i in range(start, end + 1):
            if i < len(props) and props[i] == 0:
                props[i] = val
                
    # 3. InCB Properties (Overlay - High Priority for Indic)
    # If something is InCB_Linker, it acts as Extend for general rules but has special behavior for GB9c.
    # We should probably give it a distinct value (which we did: 15, 16, 17).
    # But wait! If we change its value from EXTEND to INCB_LINKER, we break GB9 (x Extend).
    # segments.py needs to handle INCB_LINKER as if it were EXTEND for GB9.
    # So we assign a NEW value, and update segments.py to treat it correctly.
    
    for start, end, prop in incb_ranges:
        val = prop_to_int.get(prop)
        for i in range(start, end + 1):
            if i < len(props):
                # We overwrite! This is crucial.
                # A character can be both Extend and InCB_Linker.
                # BUT, do not overwrite ZWJ (13) because GB11 relies on specific ZWJ identity.
                if props[i] == prop_to_int['ZWJ']:
                    continue
                    
                props[i] = val

    # Compress
    final_table: List[Tuple[int, str]] = []
    current_val = -1
    int_to_prop = {v: k for k, v in prop_to_int.items()}
    
    for i in range(len(props)):
        val = props[i]
        if val != current_val:
            prop_name = int_to_prop.get(val, 'Other')
            final_table.append((i, prop_name))
            current_val = val
            
    print(f"Generated {len(final_table)} break property ranges.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(HEADER)
        f.write("\n")
        f.write("# Sorted list of (start_codepoint, property_constant)\n")
        f.write("# Use bisect.bisect_right to find the index\n")
        f.write("GRAPHEME_BREAK_RANGES: Final[tuple[tuple[int, int], ...]] = (\n")
        
        for start, prop_name in final_table:
            f.write(f"    ({start}, {prop_name.upper()}),\n")
            
        f.write(")\n")
        
    print(f"Written to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate()
