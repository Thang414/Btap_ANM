"""
Unit Tests for Security Guardrails
Validates Path Traversal protection and strict sandbox boundary enforcement.
"""

import pytest
from config import validate_sandbox_path, SecurityGuardException, SANDBOX_DIR


def test_valid_sandbox_path():
    """Paths inside sandbox must be allowed."""
    valid_file = SANDBOX_DIR / "sample.txt"
    resolved = validate_sandbox_path("sample.txt")
    assert resolved == valid_file.resolve()


def test_path_traversal_double_dot():
    """Attempts to traverse upwards with '..' must be blocked immediately."""
    with pytest.raises(SecurityGuardException):
        validate_sandbox_path("../../config.py")


def test_absolute_system_path():
    """Attempts to point to system paths outside sandbox must be blocked."""
    with pytest.raises(SecurityGuardException):
        validate_sandbox_path("C:\\Windows\\System32\\cmd.exe")


def test_root_traversal():
    """Attempts to traverse to filesystem root must be blocked."""
    with pytest.raises(SecurityGuardException):
        validate_sandbox_path("/etc/passwd")
