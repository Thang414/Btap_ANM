"""
Blue Team Defense Engine
Includes:
1. Canary / Honeypot Decoy Tripwires
2. File Integrity Monitoring (FIM)
3. Automated Snapshot & Rollback (Shadow Copy Simulation)
4. Real-time Security Event Audit Logging
"""

import os
import shutil
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import (
    SANDBOX_DIR,
    SNAPSHOTS_DIR,
    RANSOM_EXTENSION,
    RANSOM_NOTE_NAME,
    validate_sandbox_path,
)


CANARY_DEFINITIONS = [
    {
        "filename": "!00_CANARY_FINANCE_2026.docx",
        "description": "Tệp mồi nhử tài chính (Tên bắt đầu bằng !00 để ransomware duyệt đầu tiên)",
        "content": b"TOP SECRET: Q4 Financial Budget and Executive Bonuses 2026. Strictly Confidential.",
    },
    {
        "filename": "~_HONEYPOT_PASSWORDS.txt",
        "description": "Tệp mật khẩu bẫy thu hút attacker/malware",
        "content": b"admin:SuperSecret2026!\nroot:toor\ndb_cluster:ProductionMasterKey99!",
    },
]


class DefenseEngine:
    def __init__(self):
        self.audit_logs: List[Dict[str, Any]] = []
        self.baseline_hashes: Dict[str, str] = {}
        self.snapshots_dir = SNAPSHOTS_DIR
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.log_event("SYSTEM", "Khởi tạo hệ thống phòng thủ Blue Team thành công.", "INFO")

    def log_event(self, category: str, message: str, severity: str = "INFO", details: Optional[Dict] = None) -> None:
        """Appends an event to the security audit trail."""
        event = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "category": category,
            "message": message,
            "severity": severity,  # INFO, WARNING, CRITICAL, SUCCESS
            "details": details or {},
        }
        self.audit_logs.insert(0, event)  # newest first
        if len(self.audit_logs) > 200:
            self.audit_logs.pop()

    def get_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent security events."""
        return self.audit_logs[:limit]

    def plant_canaries(self) -> List[Dict[str, Any]]:
        """Plants canary/honeypot decoy files into the sandbox directory."""
        planted = []
        for canary in CANARY_DEFINITIONS:
            file_path = SANDBOX_DIR / canary["filename"]
            with open(file_path, "wb") as f:
                f.write(canary["content"])
            planted.append({
                "filename": canary["filename"],
                "description": canary["description"],
                "sha256": hashlib.sha256(canary["content"]).hexdigest(),
                "status": "ARMED",
            })
        self.log_event("DEFENSE", f"Đã kích hoạt {len(planted)} tệp mồi nhử (Canary Tripwires).", "INFO")
        return planted

    def check_canaries(self) -> Dict[str, Any]:
        """
        Inspects the status of canary decoy files.
        If any canary file is missing, modified, or appended with .locked,
        triggers an immediate intrusion alarm!
        """
        results = []
        any_tripped = False

        for canary in CANARY_DEFINITIONS:
            orig_name = canary["filename"]
            orig_path = SANDBOX_DIR / orig_name
            locked_path = SANDBOX_DIR / (orig_name + RANSOM_EXTENSION)
            expected_hash = hashlib.sha256(canary["content"]).hexdigest()

            if locked_path.exists():
                status = "TRIPPED_ENCRYPTED"
                reason = f"Tệp mồi nhử đã bị mã hóa thành '{locked_path.name}'!"
                any_tripped = True
            elif not orig_path.exists():
                status = "TRIPPED_DELETED"
                reason = "Tệp mồi nhử đã bị xóa hoặc đổi tên bất thường!"
                any_tripped = True
            else:
                with open(orig_path, "rb") as f:
                    curr_hash = hashlib.sha256(f.read()).hexdigest()
                if curr_hash != expected_hash:
                    status = "TRIPPED_MODIFIED"
                    reason = "Nội dung tệp mồi nhử đã bị can thiệp trái phép!"
                    any_tripped = True
                else:
                    status = "ARMED_INTACT"
                    reason = "Bẫy an toàn, chưa bị xâm phạm."

            results.append({
                "filename": orig_name,
                "description": canary["description"],
                "status": status,
                "reason": reason,
                "is_tripped": status != "ARMED_INTACT",
            })

        if any_tripped:
            self.log_event(
                "ALERT",
                "CẢNH BÁO XÂM NHẬP: Phát hiện tệp mồi nhử Canary bị tác động! Khả năng ransomware đang thực thi.",
                "CRITICAL",
                {"canaries": results},
            )

        return {
            "canary_count": len(results),
            "any_tripped": any_tripped,
            "canaries": results,
            "overall_status": "DANGER" if any_tripped else "SECURE",
        }

    def create_snapshot(self, snapshot_name: str = "baseline_snapshot") -> Dict[str, Any]:
        """
        Creates a clean shadow snapshot of the sandbox files for rapid disaster recovery.
        """
        target_dir = self.snapshots_dir / snapshot_name
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        copied_count = 0
        total_bytes = 0

        for item in SANDBOX_DIR.iterdir():
            if item.is_file() and not item.name.endswith(RANSOM_EXTENSION) and item.name != RANSOM_NOTE_NAME:
                shutil.copy2(item, target_dir / item.name)
                copied_count += 1
                total_bytes += item.stat().st_size

        self.log_event(
            "SNAPSHOT",
            f"Đã tạo bản sao lưu Snapshot '{snapshot_name}' gồm {copied_count} tệp sạch ({total_bytes} bytes).",
            "SUCCESS",
        )

        return {
            "success": True,
            "snapshot_name": snapshot_name,
            "files_copied": copied_count,
            "total_bytes": total_bytes,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def rollback_snapshot(self, snapshot_name: str = "baseline_snapshot") -> Dict[str, Any]:
        """
        Restores sandbox directory from the specified clean snapshot.
        Eliminates any .locked files or ransom notes and restores clean original files.
        """
        source_dir = self.snapshots_dir / snapshot_name
        if not source_dir.exists():
            raise FileNotFoundError(f"Snapshot '{snapshot_name}' does not exist.")

        # Clear existing sandbox contents
        for item in SANDBOX_DIR.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        # Restore from snapshot
        restored_count = 0
        for item in source_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, SANDBOX_DIR / item.name)
                restored_count += 1

        self.log_event(
            "ROLLBACK",
            f"Đã phục hồi toàn bộ dữ liệu Sandbox từ Snapshot '{snapshot_name}' ({restored_count} tệp được khôi phục).",
            "SUCCESS",
        )

        return {
            "success": True,
            "snapshot_name": snapshot_name,
            "restored_files_count": restored_count,
            "restored_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
