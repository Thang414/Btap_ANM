"""
Unit Tests for Blue Team Defense Modules
Validates Canary Tripwires and Snapshot / Rollback Disaster Recovery.
"""

import pytest
from config import SANDBOX_DIR, RANSOM_EXTENSION
from app.core.defense_engine import DefenseEngine
from app.core.seed_data import reset_sandbox_environment


@pytest.fixture
def defense_env():
    engine = DefenseEngine()
    reset_sandbox_environment(engine)
    return engine


def test_canaries_armed_initially(defense_env):
    """Initially planted canaries must be ARMED and INTACT."""
    status = defense_env.check_canaries()
    assert status["any_tripped"] is False
    assert status["overall_status"] == "SECURE"


def test_canary_tripped_when_encrypted(defense_env):
    """Canary must report TRIPPED when renamed to .locked."""
    canary_path = SANDBOX_DIR / "!00_CANARY_FINANCE_2026.docx"
    locked_path = SANDBOX_DIR / ("!00_CANARY_FINANCE_2026.docx" + RANSOM_EXTENSION)

    canary_path.rename(locked_path)

    status = defense_env.check_canaries()
    assert status["any_tripped"] is True
    assert status["overall_status"] == "DANGER"

    # Clean up
    if locked_path.exists():
        locked_path.unlink()


def test_snapshot_and_rollback(defense_env):
    """Verifies that rollback restores files deleted or changed in the sandbox."""
    defense_env.create_snapshot("test_snapshot")

    # Tamper with sandbox: delete all files
    for f in SANDBOX_DIR.iterdir():
        if f.is_file():
            f.unlink()

    assert len(list(SANDBOX_DIR.iterdir())) == 0

    # Rollback
    res = defense_env.rollback_snapshot("test_snapshot")
    assert res["success"] is True
    assert len(list(SANDBOX_DIR.iterdir())) > 0
