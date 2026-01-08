import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from indium import segments
from indium._grapheme_data import (
    GRAPHEME_BREAK_RANGES, EXTENDED_PICTOGRAPHIC,
    INCB_LINKER, INCB_CONSONANT, INCB_EXTEND,
    OTHER
)

chars = {
    'Virama (094D)': 0x094D,
    'Ka (0915)': 0x0915,
    'Ta (0924)': 0x0924,
    'Baby (1F476)': 0x1F476,
    'Stop (1F6D1)': 0x1F6D1,
    'SkinTone (1F3FF)': 0x1F3FF,
    'ZWJ (200D)': 0x200D,
}

print("Property values:")
for name, cp in chars.items():
    prop = segments._get_break_property(cp)
    print(f"{name}: {prop}")

print("\nConstants:")
print(f"EXTENDED_PICTOGRAPHIC: {EXTENDED_PICTOGRAPHIC}")
print(f"INCB_LINKER: {INCB_LINKER}")
print(f"INCB_CONSONANT: {INCB_CONSONANT}")
print(f"OTHER: {OTHER}")

