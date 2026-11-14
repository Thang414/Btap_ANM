"""
Configuration & Security Policy Settings
Project: Mô phỏng Ransomware – Mã độc tống tiền
Safety Mode: 100% Isolated Local Sandbox Environment
"""

import os
from pathlib import Path


class SecurityGuardException(Exception):
    """Raised when an operation attempts to access files outside the Sandbox directory."""
    pass


# Base project paths
BASE_DIR = Path(__file__).resolve().parent
SANDBOX_DIR = BASE_DIR / "sandbox_victim"
INSTANCE_DIR = BASE_DIR / "instance"
KEYS_DIR = INSTANCE_DIR / "keys"
SNAPSHOTS_DIR = INSTANCE_DIR / "snapshots"

# Ensure runtime directories exist
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
KEYS_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Cryptographic Constants
MAGIC_HEADER = b"LOCKSIM1"
RSA_KEY_SIZE = 2048
AES_KEY_SIZE = 32          # 256 bits
AES_NONCE_SIZE = 12        # 96 bits for AES-GCM
RANSOM_EXTENSION = ".locked"
RANSOM_NOTE_NAME = "README_DECRYPT.txt"

# Security Restrictions
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB max file size for safety in sandbox
ALLOWED_EXTENSIONS = {
    ".txt", ".docx", ".xlsx", ".pdf", ".png", ".jpg",
    ".sql", ".py", ".json", ".csv", ".log", RANSOM_EXTENSION
}


def validate_sandbox_path(target_path: str | Path) -> Path:
    """
    Path Traversal Guard:
    Guarantees that any file manipulation is strictly confined within SANDBOX_DIR.
    Prevents path traversal attacks (e.g. '../', absolute paths pointing to system files).
    """
    resolved_sandbox = SANDBOX_DIR.resolve()
    
    if isinstance(target_path, str):
        path_obj = Path(target_path.strip())
        if path_obj.is_absolute() or target_path.startswith("/") or target_path.startswith("\\"):
            candidate = path_obj.resolve()
        else:
            candidate = (SANDBOX_DIR / path_obj).resolve()
    else:
        candidate = target_path.resolve()

    try:
        # relative_to will throw ValueError if candidate is not strictly inside resolved_sandbox
        candidate.relative_to(resolved_sandbox)
    except ValueError:
        raise SecurityGuardException(
            f"ACCESS DENIED: Path '{candidate}' is outside the authorized sandbox '{resolved_sandbox}'."
        )

    return candidate
