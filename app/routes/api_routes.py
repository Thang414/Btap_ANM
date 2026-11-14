"""
RESTful API Routes for Ransomware Attack & Defense Simulator
All file actions are strictly secured by Path Traversal Guardrails.
"""

import hashlib
import time
from pathlib import Path
from flask import Blueprint, jsonify, request, current_app

from config import (
    SANDBOX_DIR,
    RANSOM_EXTENSION,
    RANSOM_NOTE_NAME,
    validate_sandbox_path,
    SecurityGuardException,
)
from app.core.entropy_engine import EntropyEngine
from app.core.seed_data import reset_sandbox_environment

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _get_crypto_engine():
    return current_app.extensions["crypto_engine"]


def _get_defense_engine():
    return current_app.extensions["defense_engine"]


@api_bp.route("/sandbox/files", methods=["GET"])
def list_sandbox_files():
    """Returns detailed status and metadata of all files in the sandbox."""
    crypto = _get_crypto_engine()
    files_data = []

    for item in sorted(SANDBOX_DIR.iterdir(), key=lambda x: x.name.lower()):
        if not item.is_file():
            continue

        size = item.stat().st_size
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item.stat().st_mtime))
        is_locked = item.name.endswith(RANSOM_EXTENSION)
        is_canary = item.name.startswith("!") or item.name.startswith("~")
        is_note = item.name == RANSOM_NOTE_NAME

        # Calculate quick hash and entropy
        with open(item, "rb") as f:
            content = f.read()
        sha256 = hashlib.sha256(content).hexdigest()
        entropy = EntropyEngine.calculate_entropy(content)

        files_data.append({
            "name": item.name,
            "size": size,
            "modified_at": mtime,
            "is_locked": is_locked,
            "is_canary": is_canary,
            "is_ransom_note": is_note,
            "sha256": sha256,
            "entropy": entropy,
            "risk_level": "CRITICAL" if is_locked or entropy >= 7.6 else ("WARNING" if entropy >= 6.5 else "NORMAL"),
        })

    return jsonify({
        "success": True,
        "files_count": len(files_data),
        "files": files_data,
        "locked_count": sum(1 for f in files_data if f["is_locked"]),
    })


@api_bp.route("/sandbox/file-preview", methods=["GET"])
def get_file_preview():
    """Returns a safe text or hex preview of a sandbox file."""
    filename = request.args.get("filename", "")
    try:
        safe_path = validate_sandbox_path(filename)
        if not safe_path.exists() or not safe_path.is_file():
            return jsonify({"success": False, "error": "Tệp không tồn tại."}), 404

        with open(safe_path, "rb") as f:
            raw_data = f.read(4096)  # Read up to 4KB preview

        is_binary = b"\x00" in raw_data
        entropy = EntropyEngine.calculate_entropy(raw_data)

        if not is_binary:
            try:
                preview_text = raw_data.decode("utf-8")
                preview_type = "text"
            except UnicodeDecodeError:
                preview_text = raw_data.hex(" ", 16)
                preview_type = "hex"
        else:
            preview_text = raw_data.hex(" ", 16)
            preview_type = "hex"

        return jsonify({
            "success": True,
            "filename": safe_path.name,
            "file_size": safe_path.stat().st_size,
            "preview_type": preview_type,
            "preview_content": preview_text[:2000],
            "entropy": entropy,
        })
    except SecurityGuardException as e:
        return jsonify({"success": False, "error": str(e)}), 403
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/simulate/encrypt-file", methods=["POST"])
def simulate_encrypt_file():
    """Simulates Ransomware Hybrid Encryption on a single target file."""
    crypto = _get_crypto_engine()
    defense = _get_defense_engine()
    data = request.get_json() or {}
    filename = data.get("filename")

    if not filename:
        return jsonify({"success": False, "error": "Thiếu tham số 'filename'."}), 400

    try:
        safe_path = validate_sandbox_path(filename)
        result = crypto.encrypt_file(safe_path)

        # Log attack event
        defense.log_event(
            "ATTACK",
            f"Mã hóa tệp thành công: '{result['original_filename']}' -> '{result['locked_filename']}' (AES-256-GCM + RSA-2048)",
            "CRITICAL",
            result,
        )

        # Automatically check if a canary was tripped
        canary_status = defense.check_canaries()

        return jsonify({
            "success": True,
            "result": result,
            "canary_alert": canary_status["any_tripped"],
        })
    except SecurityGuardException as e:
        return jsonify({"success": False, "error": str(e)}), 403
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@api_bp.route("/simulate/encrypt-all", methods=["POST"])
def simulate_encrypt_all():
    """Simulates Ransomware mass-encryption across the sandbox."""
    crypto = _get_crypto_engine()
    defense = _get_defense_engine()

    try:
        result = crypto.encrypt_all_sandbox()
        defense.log_event(
            "ATTACK_MASS",
            f"ĐỢT TẤN CÔNG DIỆN RỘNG: Đã mã hóa {result['total_files_encrypted']} tệp tin trong thư mục Sandbox!",
            "CRITICAL",
            result,
        )

        canary_status = defense.check_canaries()

        return jsonify({
            "success": True,
            "result": result,
            "canary_alert": canary_status["any_tripped"],
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/simulate/decrypt-file", methods=["POST"])
def simulate_decrypt_file():
    """Decrypts a single .locked file using the supplied RSA Private Key."""
    crypto = _get_crypto_engine()
    defense = _get_defense_engine()
    data = request.get_json() or {}

    filename = data.get("filename")
    private_key_pem = data.get("private_key_pem", "").strip()

    if not filename or not private_key_pem:
        return jsonify({"success": False, "error": "Cần cung cấp đầy đủ 'filename' và 'private_key_pem'."}), 400

    try:
        safe_path = validate_sandbox_path(filename)
        result = crypto.decrypt_file(safe_path, private_key_pem)

        defense.log_event(
            "DECRYPT",
            f"Giải mã và khôi phục thành công: '{result['locked_filename']}' -> '{result['restored_filename']}'",
            "SUCCESS",
            result,
        )

        return jsonify({"success": True, "result": result})
    except SecurityGuardException as e:
        return jsonify({"success": False, "error": str(e)}), 403
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@api_bp.route("/simulate/decrypt-all", methods=["POST"])
def simulate_decrypt_all():
    """Decrypts all .locked files in the sandbox using the supplied private key."""
    crypto = _get_crypto_engine()
    defense = _get_defense_engine()
    data = request.get_json() or {}

    private_key_pem = data.get("private_key_pem", "").strip()
    if not private_key_pem:
        # If user left empty in lab mode, optionally provide default attacker private key
        private_key_pem = crypto.get_private_key_pem()

    try:
        result = crypto.decrypt_all_sandbox(private_key_pem)
        defense.log_event(
            "DECRYPT_MASS",
            f"Khôi phục hàng loạt thành công: {result['total_files_decrypted']} tệp đã được phục hồi nguyên vẹn.",
            "SUCCESS",
            result,
        )
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@api_bp.route("/defense/entropy-scan", methods=["GET"])
def get_entropy_scan():
    """Returns full Shannon entropy scan report of all files in sandbox."""
    try:
        report = EntropyEngine.scan_sandbox()
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/defense/canary-status", methods=["GET"])
def get_canary_status():
    """Returns the integrity status of canary decoy tripwire files."""
    defense = _get_defense_engine()
    try:
        status = defense.check_canaries()
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/defense/snapshot/create", methods=["POST"])
def create_snapshot():
    """Creates a clean snapshot of sandbox files."""
    defense = _get_defense_engine()
    data = request.get_json() or {}
    name = data.get("snapshot_name", "manual_snapshot")
    try:
        res = defense.create_snapshot(name)
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/defense/snapshot/rollback", methods=["POST"])
def rollback_snapshot():
    """Restores sandbox directory from the clean snapshot."""
    defense = _get_defense_engine()
    data = request.get_json() or {}
    name = data.get("snapshot_name", "baseline_snapshot")
    try:
        res = defense.rollback_snapshot(name)
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@api_bp.route("/sandbox/reset", methods=["POST"])
def reset_sandbox():
    """1-Click Reset: purges sandbox and re-seeds clean dummy files."""
    defense = _get_defense_engine()
    try:
        res = reset_sandbox_environment(defense)
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/c2/keys", methods=["GET"])
def get_c2_keys():
    """Returns the C2 Attacker Public and Private keys for educational inspection."""
    crypto = _get_crypto_engine()
    return jsonify({
        "success": True,
        "public_key_pem": crypto.get_public_key_pem(),
        "private_key_pem": crypto.get_private_key_pem(),
        "fingerprint": crypto.get_key_fingerprint(),
    })


@api_bp.route("/audit-logs", methods=["GET"])
def get_audit_logs():
    """Returns the security audit log stream."""
    defense = _get_defense_engine()
    return jsonify({
        "success": True,
        "logs": defense.get_audit_logs(limit=100),
    })
