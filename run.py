"""
Application Entry Point
Project: Mô phỏng Ransomware – Mã độc tống tiền
Interactive Security Lab & Attack/Defense Simulator
"""

import sys
from app import create_app
from config import SANDBOX_DIR

app = create_app()

if __name__ == "__main__":
    port = 5000
    host = "127.0.0.1"

    print("=" * 75)
    print("  ĐỒ ÁN MÔN HỌC: AN NINH MẠNG / AN TOÀN THÔNG TIN")
    print("  ĐỀ TÀI: MÔ PHỎNG RANSOMWARE – MÃ ĐỘC TỐNG TIỀN")
    print("  Attack & Defense Interactive Simulator (100% Local Sandbox)")
    print("=" * 75)
    print(f"  [+] Sandbox Path : {SANDBOX_DIR.resolve()}")
    print(f"  [+] Web Dashboard: http://{host}:{port}")
    print("  [+] Nút '1-Click Reset Sandbox' luôn khả dụng trên giao diện.")
    print("=" * 75)
    print("  Nhấn CTRL+C để dừng server.\n")

    app.run(host=host, port=port, debug=True)
