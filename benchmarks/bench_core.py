"""Performance benchmarks for indium core functions.

Run with:
    python3 -m pytest benchmarks/bench_core.py
    OR
    python3 benchmarks/bench_core.py
"""

import timeit
import indium

def benchmark_is_mixed_script():
    """Compare performance of mixed script detection on ASCII vs Unicode."""
    ascii_text = "Hello World" * 100
    unicode_text = "Hello World" * 99 + "φ"  # One Greek char at end
    mixed_text = "Hello World φ" * 50
    
    print("\n[is_mixed_script]")
    
    t_ascii = timeit.timeit(lambda: indium.is_mixed_script(ascii_text), number=10000)
    print(f"ASCII (Fast Path): {t_ascii:.4f}s")
    
    t_uni = timeit.timeit(lambda: indium.is_mixed_script(unicode_text), number=10000)
    print(f"Unicode (Latin+Greek): {t_uni:.4f}s")
    
    t_mixed = timeit.timeit(lambda: indium.is_mixed_script(mixed_text), number=10000)
    print(f"Mixed (Many switches): {t_mixed:.4f}s")

def benchmark_skeleton():
    """Benchmark visual normalization."""
    ascii_text = "paypal" * 100
    spoof_text = "pаypal" * 100  # Cyrillic 'a'
    
    print("\n[skeleton]")
    
    t_ascii = timeit.timeit(lambda: indium.skeleton(ascii_text), number=1000)
    print(f"ASCII (Fast Path): {t_ascii:.4f}s")
    
    t_spoof = timeit.timeit(lambda: indium.skeleton(spoof_text), number=1000)
    print(f"Spoof (Normalization): {t_spoof:.4f}s")

def benchmark_graphemes():
    """Benchmark grapheme counting."""
    ascii_text = "Hello World" * 100
    emoji_text = "👨‍👩‍👧" * 100  # Family emoji
    
    print("\n[count_graphemes]")
    
    t_ascii = timeit.timeit(lambda: indium.count_graphemes(ascii_text), number=1000)
    print(f"ASCII: {t_ascii:.4f}s")
    
    t_emoji = timeit.timeit(lambda: indium.count_graphemes(emoji_text), number=1000)
    print(f"Emoji Sequences: {t_emoji:.4f}s")

if __name__ == "__main__":
    print(f"Indium v{indium.__version__} Benchmarks")
    benchmark_is_mixed_script()
    benchmark_skeleton()
    benchmark_graphemes()
