"""
Seed Data & Sandbox Reset Service
Generates realistic dummy files for student laboratory experiments.
Provides 1-Click Sandbox Environment Reset capability.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any

from config import SANDBOX_DIR, RANSOM_NOTE_NAME, RANSOM_EXTENSION


# Minimal valid 1x1 transparent PNG file binary
TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
    b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

# Minimal valid PDF header and structure
MOCK_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
    b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
    b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n185\n%%EOF\n"
)


SAMPLE_FILES = [
    {
        "filename": "financial_q4_summary.xlsx",
        "content": (
            "Quarter,Department,Budget_USD,Actual_USD,Variance_USD\n"
            "Q1,Research & Development,450000,420000,+30000\n"
            "Q2,Cybersecurity Ops,300000,310000,-10000\n"
            "Q3,Cloud Infrastructure,600000,580000,+20000\n"
            "Q4,Executive & Legal,250000,240000,+10000\n"
            "Total,All Divisions,1600000,1550000,+50000\n"
        ).encode("utf-8"),
    },
    {
        "filename": "customer_database.sql",
        "content": (
            "-- Database Dump: Customer Information 2026\n"
            "CREATE TABLE customers (\n"
            "    id INT PRIMARY KEY AUTO_INCREMENT,\n"
            "    full_name VARCHAR(100),\n"
            "    email VARCHAR(100),\n"
            "    card_token VARCHAR(64),\n"
            "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
            ");\n\n"
            "INSERT INTO customers (full_name, email, card_token) VALUES\n"
            "('Nguyen Van An', 'an.nguyen@corporation.vn', 'tok_visa_89234872138'),\n"
            "('Tran Thi Binh', 'binh.tran@techgroup.vn', 'tok_mc_98374928173'),\n"
            "('Le Hoang Minh', 'minh.le@vietsecurity.edu.vn', 'tok_jcb_12938172938');\n"
        ).encode("utf-8"),
    },
    {
        "filename": "ceo_strategy_memo.txt",
        "content": (
            "THONG DIEP NOI BO - MAT CHUYEN MON\n"
            "Kinh gui: Hoi dong Quan tri & Ban Tong Giam doc\n\n"
            "1. Muc tieu nang cap ha tang bao mat quy 4:\n"
            "   - Trien khai giai phap giam sat toan ven tap tin (File Integrity Monitoring - FIM).\n"
            "   - Cai dat he thong phat hien ma hoa bat thuong dua tren Shannon Entropy.\n"
            "   - Bo tri cac tap tin moi nhu (Canary/Honeypot) tren toan bo may chu luu tru.\n\n"
            "2. Chinh sach sao luu bat kha bien (Immutable Backups):\n"
            "   - Toan bo snapshot du lieu phai duoc luu tren may chu cach ly (Air-gapped).\n"
            "   - Thuong xuyen dien tap quy trinh phuc hoi sau tham hoa ma doc tong tien.\n\n"
            "Tong Giam Doc ky duyet\n"
        ).encode("utf-8"),
    },
    {
        "filename": "server_credentials.json",
        "content": (
            "{\n"
            '  "environment": "production-cluster-01",\n'
            '  "primary_db_host": "db.corp.internal:5432",\n'
            '  "api_auth_secret": "sec_k8s_98d7f6a5b4c3e210fedcba9876543210",\n'
            '  "backup_vault_url": "s3://corp-backups-immutable-2026/",\n'
            '  "rotation_period_days": 30\n'
            "}\n"
        ).encode("utf-8"),
    },
    {
        "filename": "payment_gateway_api.py",
        "content": (
            "# Payment Gateway Microservice Core Module\n"
            "import hmac\nimport hashlib\nimport time\n\n"
            "def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:\n"
            '    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()\n'
            "    return hmac.compare_digest(expected, signature)\n\n"
            "def process_transaction(order_id: str, amount_cents: int) -> dict:\n"
            '    return {"status": "SUCCESS", "tx_id": f"tx_{int(time.time())}_{order_id}"}\n'
        ).encode("utf-8"),
    },
    {
        "filename": "annual_security_audit.pdf",
        "content": MOCK_PDF_BYTES,
    },
    {
        "filename": "corp_infrastructure_diagram.png",
        "content": TINY_PNG_BYTES,
    },
]


def reset_sandbox_environment(defense_engine=None) -> Dict[str, Any]:
    """
    Completely purges the sandbox directory, re-creates all standard sample files,
    plants fresh canary files, and takes an automatic clean baseline snapshot.
    """
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Remove all existing files in sandbox
    for item in SANDBOX_DIR.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

    # 2. Seed standard sample files
    created_files = []
    for sample in SAMPLE_FILES:
        target = SANDBOX_DIR / sample["filename"]
        with open(target, "wb") as f:
            f.write(sample["content"])
        created_files.append(sample["filename"])

    # 3. Plant fresh canary tripwires
    if defense_engine:
        defense_engine.plant_canaries()
        defense_engine.create_snapshot("baseline_snapshot")
        defense_engine.log_event("SYSTEM", "Đã thiết lập lại (Reset) Sandbox về trạng thái ban đầu sạch sẽ.", "SUCCESS")

    return {
        "success": True,
        "message": "Sandbox environment successfully restored to clean baseline.",
        "files_created": created_files,
        "total_files": len(created_files) + 2,  # sample files + 2 canaries
    }
