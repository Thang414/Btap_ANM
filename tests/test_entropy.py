"""
Unit Tests for Shannon Entropy Calculation Engine
Validates that plaintext and ciphertext exhibit distinct mathematical entropy profiles.
"""

import os
from app.core.entropy_engine import EntropyEngine


def test_entropy_plain_text():
    """Plain repetitive text should have moderate to low entropy (< 5.0)."""
    text_data = b"Hello world! This is a standard plain text document with repetitive words and spaces."
    entropy = EntropyEngine.calculate_entropy(text_data)
    assert 3.0 <= entropy <= 5.5


def test_entropy_zero_bytes():
    """Single repeating byte must have 0 entropy."""
    data = b"\x00" * 1000
    entropy = EntropyEngine.calculate_entropy(data)
    assert entropy == 0.0


def test_entropy_random_ciphertext():
    """Cryptographically random data / ciphertext must exhibit near maximum entropy (> 7.8)."""
    random_bytes = os.urandom(4096)
    entropy = EntropyEngine.calculate_entropy(random_bytes)
    assert entropy >= 7.85


def test_byte_histogram_length():
    """Histogram must return exact number of bins requested."""
    data = os.urandom(100)
    hist = EntropyEngine.get_byte_histogram(data, bins=16)
    assert len(hist) == 16
    assert sum(hist) == 100

