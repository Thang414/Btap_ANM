"""
Integration Tests for Flask REST API Endpoints
"""

import pytest
from app import create_app
from config import SANDBOX_DIR
from app.core.seed_data import reset_sandbox_environment


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            reset_sandbox_environment(app.extensions["defense_engine"])
        yield client


def test_api_list_files(client):
    res = client.get("/api/sandbox/files")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["files_count"] > 0


def test_api_entropy_scan(client):
    res = client.get("/api/defense/entropy-scan")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "report" in data
    assert data["report"]["scanned_files_count"] > 0


def test_api_canary_status(client):
    res = client.get("/api/defense/canary-status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "status" in data


def test_api_encrypt_and_decrypt_flow(client):
    # 1. Encrypt ceo_strategy_memo.txt
    enc_res = client.post("/api/simulate/encrypt-file", json={"filename": "ceo_strategy_memo.txt"})
    assert enc_res.status_code == 200
    enc_data = enc_res.get_json()
    assert enc_data["success"] is True
    assert enc_data["result"]["locked_filename"] == "ceo_strategy_memo.txt.locked"

    # 2. Get C2 private key
    keys_res = client.get("/api/c2/keys")
    priv_key = keys_res.get_json()["private_key_pem"]

    # 3. Decrypt
    dec_res = client.post("/api/simulate/decrypt-file", json={
        "filename": "ceo_strategy_memo.txt.locked",
        "private_key_pem": priv_key
    })
    assert dec_res.status_code == 200
    dec_data = dec_res.get_json()
    assert dec_data["success"] is True
    assert dec_data["result"]["restored_filename"] == "ceo_strategy_memo.txt"


def test_api_reset_sandbox(client):
    res = client.post("/api/sandbox/reset")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True

