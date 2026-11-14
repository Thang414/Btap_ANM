"""
Entropy Analysis Engine (Shannon Entropy)
Evaluates randomness of file bytes to detect encryption anomalies.
Encrypted files exhibit near-maximum entropy (~7.9 - 8.0 bits/byte) with uniform distribution.
"""

import math
from pathlib import Path
from typing import Dict, Any, List, Tuple
from config import validate_sandbox_path, SANDBOX_DIR, RANSOM_NOTE_NAME


class EntropyEngine:
    @staticmethod
    def calculate_entropy(data: bytes) -> float:
        """
        Computes the Shannon Entropy of raw byte data.
        Returns a float between 0.0 (completely uniform/zero information)
        and 8.0 (maximal randomness / encrypted / compressed).
        """
        if not data:
            return 0.0

        length = len(data)
        byte_counts = [0] * 256
        for b in data:
            byte_counts[b] += 1

        entropy = 0.0
        for count in byte_counts:
            if count > 0:
                p_i = count / length
                entropy -= p_i * math.log2(p_i)

        return round(entropy, 4)

    @staticmethod
    def get_byte_histogram(data: bytes, bins: int = 16) -> List[int]:
        """
        Groups byte frequencies into bins (default: 16 bins, 16 values per bin)
        for efficient frontend chart visualization.
        """
        if not data:
            return [0] * bins

        bin_size = 256 // bins
        histogram = [0] * bins

        for b in data:
            bin_index = min(b // bin_size, bins - 1)
            histogram[bin_index] += 1

        return histogram

    @classmethod
    def analyze_file(cls, file_path: str | Path) -> Dict[str, Any]:
        """
        Performs full entropy and randomness analysis on a sandbox file.
        """
        safe_path = validate_sandbox_path(file_path)

        if not safe_path.exists() or not safe_path.is_file():
            raise FileNotFoundError(f"File not found: {safe_path.name}")

        with open(safe_path, "rb") as f:
            content = f.read()

        file_size = len(content)
        entropy = cls.calculate_entropy(content)
        histogram = cls.get_byte_histogram(content, bins=16)

        # Risk Classification
        if entropy >= 7.6:
            risk_level = "CRITICAL_ENCRYPTED"
            risk_label = "Nguy hiểm - Khả năng cao đã bị mã hóa"
            badge_color = "danger"
        elif entropy >= 6.5:
            risk_level = "SUSPICIOUS"
            risk_label = "Đáng ngờ - Nén cao hoặc nhị phân"
            badge_color = "warning"
        elif entropy >= 4.0:
            risk_level = "MODERATE"
            risk_label = "Bình thường - Văn bản / Mã nguồn"
            badge_color = "info"
        else:
            risk_level = "LOW"
            risk_label = "Thấp - Cấu trúc dữ liệu lặp lại cao"
            badge_color = "success"

        return {
            "filename": safe_path.name,
            "file_size": file_size,
            "entropy": entropy,
            "max_entropy": 8.0,
            "entropy_percentage": round((entropy / 8.0) * 100, 1),
            "risk_level": risk_level,
            "risk_label": risk_label,
            "badge_color": badge_color,
            "histogram": histogram,
            "is_locked": safe_path.name.endswith(".locked"),
        }

    @classmethod
    def scan_sandbox(cls) -> Dict[str, Any]:
        """
        Scans all files in the sandbox directory and provides aggregated entropy metrics.
        """
        files = [
            f for f in SANDBOX_DIR.iterdir()
            if f.is_file() and f.name != RANSOM_NOTE_NAME
        ]

        file_reports = []
        total_entropy = 0.0
        encrypted_count = 0

        for f in files:
            rep = cls.analyze_file(f)
            file_reports.append(rep)
            total_entropy += rep["entropy"]
            if rep["risk_level"] == "CRITICAL_ENCRYPTED":
                encrypted_count += 1

        avg_entropy = round(total_entropy / len(files), 3) if files else 0.0

        return {
            "scanned_files_count": len(files),
            "encrypted_files_count": encrypted_count,
            "average_entropy": avg_entropy,
            "sandbox_status": "COMPROMISED" if encrypted_count > 0 else "SECURE",
            "files": file_reports,
        }
