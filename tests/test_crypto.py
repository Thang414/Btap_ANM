"""
Unit Tests for Hybrid Cryptography Engine
Validates AES-256-GCM + RSA-2048 encryption, decryption, and SHA-256 data integrity.
"""

import os
import hashlib
import pytest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from config import SANDBOX_DIR, RANSOM_EXTENSION, RANSOM_NOTE_NAME
from app.core.crypto_engine import CryptoEngine


@pytest.fixture
def crypto_engine():
    return CryptoEngine()


@pytest.fixture
def sample_test_file():
    test_path = SANDBOX_DIR / "unit_test_doc.txt"
    original_data = b"TOP SECRET: Financial audit records and internal communications 2026."
    with open(test_path, "wb") as f:
        f.write(original_data)
    yield test_path
    # Cleanup
    if test_path.exists():
        test_path.unlink()
    locked_path = test_path.with_name(test_path.name + RANSOM_EXTENSION)
    if locked_path.exists():
        locked_path.unlink()


def test_encrypt_and_decrypt_lifecycle(crypto_engine, sample_test_file):
    """Verifies that encrypting and then decrypting a file restores 100% exact original data."""
    with open(sample_test_file, "rb") as f:
        orig_bytes = f.read()
    orig_sha256 = hashlib.sha256(orig_bytes).hexdigest()

    # 1. Encrypt
    enc_res = crypto_engine.encrypt_file(sample_test_file)
    assert enc_res["success"] is True
    assert not sample_test_file.exists()
    locked_path = sample_test_file.with_name(sample_test_file.name + RANSOM_EXTENSION)
    assert locked_path.exists()

    # 2. Decrypt using C2 Private Key
    priv_key_pem = crypto_engine.get_private_key_pem()
    dec_res = crypto_engine.decrypt_file(locked_path, priv_key_pem)

    assert dec_res["success"] is True
    assert sample_test_file.exists()
    assert not locked_path.exists()

    # 3. Checksum verification
    with open(sample_test_file, "rb") as f:
        restored_bytes = f.read()
    restored_sha256 = hashlib.sha256(restored_bytes).hexdigest()

    assert orig_sha256 == restored_sha256
    assert orig_bytes == restored_bytes


def test_decrypt_with_wrong_key_fails(crypto_engine, sample_test_file):
    """Verifies that an incorrect RSA private key cannot decrypt the file."""
    crypto_engine.encrypt_file(sample_test_file)
    locked_path = sample_test_file.with_name(sample_test_file.name + RANSOM_EXTENSION)

    # Generate an unrelated wrong key
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    wrong_pem = wrong_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    with pytest.raises(ValueError, match="Decryption failed"):
        crypto_engine.decrypt_file(locked_path, wrong_pem)

