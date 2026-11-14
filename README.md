<p align="center">
  <b>Mô phỏng Ransomware – Mã độc tống tiền</b><br>
  <i>Ransomware Attack & Defense Interactive Security Lab</i>
</p>

> **Đồ án môn học:** An Ninh Mạng / An Toàn Thông Tin  
> **Đề tài:** Mô phỏng Ransomware – Mã độc tống tiền  
> **Môi trường thực nghiệm:** 100% Local Sandbox an toàn tuyệt đối (Python Flask + Cryptography + Modern Cyber SOC Dark CSS & JS)

---

## 📌 1. Giới thiệu tổng quan & Mục tiêu đề tài

**Ransomware (Mã độc tống tiền)** là một trong những hiểm họa an ninh mạng nguy hiểm và tốn kém nhất trong kỷ nguyên số. Về bản chất kỹ thuật, các biến thể mã độc tống tiền khét tiếng như *CryptoLocker, WannaCry, Ryuk, LockBit, BlackCat* khai thác các nguyên lý mật mã học (**Cryptovirology**) nhằm tước đoạt quyền truy cập dữ liệu của nạn nhân và buộc họ phải trả tiền chuộc để có khóa giải mã.

Dự án này là một **Interactive Security Lab & Attack/Defense Simulator** chạy hoàn toàn trên máy cục bộ trong môi trường **Sandbox cô lập an toàn 100%**, cho phép sinh viên, giảng viên và chuyên gia bảo mật:
1. **Trực tiếp quan sát và thực thi** toàn bộ vòng đời tấn công của Ransomware theo chuẩn mã hóa lai (**Hybrid Encryption: AES-256-GCM + RSA-2048 OAEP**).
2. **Khám phá nguyên lý toán học** tại sao các cuộc tấn công vét cạn (Brute-force) là bất khả thi trong thực tế qua công cụ tính toán không gian khóa.
3. **Thực nghiệm 3 cơ chế phòng thủ chuyên sâu của Blue Team:**
   - **Giám sát Shannon Entropy:** Phát hiện tức thì sự đột biến độ hỗn loạn byte khi tệp tin bị mã hóa ($H(X) \approx 7.9 - 8.0$).
   - **Tệp mồi nhử Canary Tripwires:** Bố trí tệp bẫy nhằm phát hiện và kích hoạt chuông báo động trước khi mã độc chạm vào dữ liệu thật.
   - **Bản chụp bất biến (Immutable Shadow Snapshot & Rollback):** Mô phỏng cơ chế sao lưu tự động và khôi phục dữ liệu nguyên bản 1-click.
4. **Đối soát tính toàn vẹn 100%:** Xác thực mã băm `SHA-256 Checksum` trước và sau khi giải mã để chứng minh dữ liệu khôi phục không mất mát.

---

## 🛡️ 2. Nguyên tắc an toàn cốt lõi (Security Guardrails)

Hệ thống được thiết kế tuân thủ nghiêm ngặt các quy chuẩn đạo đức và an toàn thông tin:
- **Sandbox cô lập 100%:** Mọi hoạt động đọc, ghi, mã hóa chỉ diễn ra duy nhất trong thư mục `sandbox_victim/`.
- **Path Traversal Guard:** Hệ thống tích hợp bộ lọc kiểm tra bảo mật `validate_sandbox_path()`, chủ động chặn đứng mọi nỗ lực truy cập đường dẫn tương đối (`../`) hoặc đường dẫn tuyệt đối ra ngoài thư mục sandbox.
- **Nút "1-Click Reset Sandbox":** Luôn sẵn sàng trên giao diện và API `/api/sandbox/reset`, cho phép phục hồi toàn bộ dữ liệu mẫu trong 1 giây.
- **Không lây lan, không kết nối ngoài:** Không có cơ chế phát tán mạng (Worm/Propagation), không tự khởi động cùng Windows (Persistence), không kết nối Internet.

---

## 🏗️ 3. Sơ đồ kiến trúc hệ thống

```text
                             [ Trình duyệt Web Client ]
                                         │
                         [ Modern SOC Cyber Dashboard ]
           ┌─────────────────────────────┼─────────────────────────────┐
           │                             │                             │
    [ Lab 1: Tấn công ]           [ Lab 2: Phòng thủ ]          [ Lab 3: Độ phức tạp ]
  Hybrid AES-256 + RSA-2048     Shannon Entropy & Canaries     Brute-Force Feasibility
           │                             │                             │
           └─────────────────────────────┼─────────────────────────────┘
                                         │
                         [ Flask RESTful API & Security Guard ]
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        │                                                                 │
 [ Crypto Engine ]            [ Entropy Engine ]               [ Defense Engine ]
 - AES-256-GCM                - Shannon Entropy H(X)           - Canary Tripwires
 - RSA-2048 OAEP              - 16-Bin Byte Histogram          - Shadow Snapshots
 - Package .locked            - Risk Classification            - Audit Trail Logs
        │                                                                 │
        └────────────────────────────────┬────────────────────────────────┘
                                         │
                             [ Local Sandbox Filesystem ]
                                  (sandbox_victim/)
                   - financial_q4_summary.xlsx
                   - customer_database.sql
                   - ceo_strategy_memo.txt
                   - !00_CANARY_FINANCE_2026.docx (Bẫy mồi nhử)
                   - ~_HONEYPOT_PASSWORDS.txt (Bẫy mồi nhử)
```

---

## 💻 4. Công nghệ sử dụng

| Thành phần | Công nghệ | Mục đích |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+ / Flask 3.1 | Xây dựng RESTful API và quản lý luồng điều khiển |
| **Mật mã học** | `cryptography` (hazmat) | AES-256-GCM (khóa phiên đối xứng), RSA-2048 OAEP SHA-256 |
| **Toán học Entropy** | Shannon Entropy Algorithm | Tính toán độ hỗn loạn $H(X) = -\sum P(x)\log_2 P(x)$ và phân bố tần suất byte |
| **Frontend** | HTML5, CSS3, Vanilla JS, Canvas API | Giao diện SOC Dark Mode, biểu đồ trực quan, không phụ thuộc CDN ngoài |
| **Kiểm thử tự động** | Pytest 9.2 | Bộ test suite 18 ca kiểm thử tự động đạt 100% Pass |
| **Script tiện ích** | Windows Batch Script | `run.bat` chạy 1-click & `test.bat` kiểm thử tự động 1-click |

---

## 📁 5. Cấu trúc mã nguồn

```text
ANM_BAITAP/
│
├── run.bat                      # Script khởi chạy ứng dụng 1-click trên Windows
├── test.bat                     # Script chạy 18 ca test tự động 1-click trên Windows
├── run.py                       # File khởi chạy Flask server chính
├── config.py                    # Cấu hình Sandbox, Security Guardrails và hằng số mã hóa
├── requirements.txt             # Thư viện phụ thuộc (Flask, cryptography, pytest)
├── README.md                    # Tài liệu báo cáo đồ án chi tiết
├── .gitignore                   # Loại trừ file tạm, cache và runtime
│
├── app/
│   ├── __init__.py              # Application Factory, gắn kết các Engine
│   ├── core/                    # Engine cốt lõi
│   │   ├── __init__.py
│   │   ├── crypto_engine.py     # Engine mã hóa lai AES-256-GCM + RSA-2048
│   │   ├── entropy_engine.py    # Engine tính Shannon Entropy & biểu đồ tần suất byte
│   │   ├── defense_engine.py    # Engine tệp mồi nhử Canary, FIM và Snapshot
│   │   └── seed_data.py         # Khởi tạo tệp mẫu & Dịch vụ Reset Sandbox
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main_routes.py       # Render các trang giao diện Dashboard & Labs
│   │   └── api_routes.py        # Các API RESTful điều khiển Sandbox
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css         # Dark Cyber Theme (Glassmorphism, Neon Green/Red)
│   │   └── js/
│   │       └── main.js          # Xử lý tương tác API, Toast Notifications & Modals
│   │
│   └── templates/
│       ├── base.html            # Layout chung, Navigation bar & Threat Alert Banner
│       ├── index.html           # Trung tâm giám sát SOC Dashboard & File Explorer
│       ├── attack_lab.html      # Lab 1: Vòng đời tấn công & Mã hóa lai từng bước
│       ├── defense_lab.html     # Lab 2: Cơ chế phòng thủ Blue Team & Shannon Entropy
│       ├── calculator.html      # Lab 3: Máy tính độ bất khả thi phá khóa Brute-force
│       └── theory.html          # Lý thuyết Cryptovirology & Khung MITRE ATT&CK
│
├── sandbox_victim/              # Thư mục nạn nhân giả lập (chứa dummy files)
└── tests/                       # Bộ kiểm thử tự động (Pytest)
    ├── test_crypto.py           # Kiểm tra mã hóa, giải mã & toàn vẹn SHA-256
    ├── test_entropy.py          # Kiểm tra độ chính xác thuật toán Shannon Entropy
    ├── test_security_guard.py   # Kiểm tra cơ chế chống Path Traversal
    ├── test_defense.py          # Kiểm tra kích hoạt bẫy Canary & Rollback Snapshot
    └── test_api.py              # Kiểm tra toàn diện các API RESTful
```

---

## 🚀 6. Hướng dẫn cài đặt & Khởi chạy

### Cách 1: Khởi chạy 1-Click trên Windows (Khuyên dùng)
1. Nhấp đúp chuột vào tệp `run.bat`.
2. Mở trình duyệt web và truy cập địa chỉ: **`http://127.0.0.1:5000`**

### Cách 2: Khởi chạy bằng dòng lệnh Terminal
```bash
# 1. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 2. Khởi chạy ứng dụng
python run.py
```

### Cách 3: Chạy bộ kiểm thử tự động
* Nhấp đúp chuột vào tệp `test.bat` hoặc chạy lệnh:
```bash
python -m pytest -v
```
*(Kết quả: 18/18 ca kiểm thử đạt 100% PASSED)*

---

## 🎯 7. Kịch bản Demo thuyết trình trước Giảng viên

Để đạt điểm số tối đa trong buổi bảo vệ đồ án, bạn hãy thực hiện theo trình tự demo sau:

1. **Bước 1 - Giới thiệu Tổng quan (Dashboard):**
   - Mở trang chủ `Dashboard`. Giới thiệu danh mục các tệp tin trong thư mục `sandbox_victim/` (văn bản tài chính, database dump, source code, và 2 tệp mồi nhử Canary).
   - Nhấn **"👁️ Xem"** vào tệp `ceo_strategy_memo.txt` để chứng minh đây là văn bản đọc được rõ ràng.
2. **Bước 2 - Thực nghiệm Mô phỏng Mã hóa (Lab 1: Attack Lifecycle):**
   - Chuyển sang menu **"⚔️ Lab 1: Tấn công (Mã hóa lai)"**.
   - Chọn tệp `financial_q4_summary.xlsx` và nhấn **"▶️ Bắt đầu mô phỏng"**.
   - Quan sát hiệu ứng diễn giải 5 bước: Đọc tệp $\rightarrow$ Sinh ngẫu nhiên khóa phiên AES-256 $\rightarrow$ Mã hóa dữ liệu bằng AES-GCM $\rightarrow$ Bọc khóa AES bằng RSA-2048 Public Key $\rightarrow$ Đóng gói thành `.locked` và thả tệp tống tiền `README_DECRYPT.txt`.
   - Mở tệp `.locked` để giảng viên thấy dữ liệu đã bị biến đổi thành mã nhị phân không thể đọc được.
3. **Bước 3 - Kiểm chứng Phòng thủ Blue Team (Lab 2: Defense & Entropy):**
   - Chuyển sang menu **"🛡️ Lab 2: Phòng thủ & Entropy"**.
   - Nhấn **"🔍 Quét Toàn Diện Entropy"**. Chỉ cho giảng viên thấy: tệp văn bản sạch có entropy thấp ($\approx 4.0 - 5.0$), trong khi tệp bị khóa có entropy tiệm cận tối đa ($\approx 7.9 - 8.0$).
   - Cho giảng viên xem **Biểu đồ phân bố tần suất byte (Byte Histogram)**: tệp mã hóa có đồ thị phẳng đồng đều tuyệt đối (Uniform Distribution).
   - Quay lại Dashboard nhấn **"☣️ Mô phỏng Mã hóa Toàn bộ"**. Quan sát ngay lập tức **Báo động đỏ (Threat Alert Banner)** nhấp nháy vì tệp mồi nhử `!00_CANARY_FINANCE_2026.docx` đã bị kích hoạt!
4. **Bước 4 - Khôi phục Dữ liệu (Decryption & Rollback):**
   - Nhấn nút **"🔑 Mở khóa"** trên tệp bị khóa, nhấn **"📋 Điền nhanh Khóa C2"** và bấm **"Giải mã tệp"**.
   - Chứng minh tệp phục hồi nguyên trạng, mã băm `SHA-256` trùng khớp 100% với tệp gốc ban đầu.
   - Thử nghiệm nút **"⏪ Rollback"** hoặc **"🔄 Reset Sandbox"** để minh họa khả năng ứng phó sự cố và khôi phục sau thảm họa.
5. **Bước 5 - Giải thích Toán học (Lab 3: Độ bất khả thi Brute-Force):**
   - Chuyển sang menu **"🧮 Lab 3"**, kéo thanh trượt so sánh giữa DES 56-bit (phá trong vài giờ) và AES 256-bit ($> 10^{50}$ năm - vượt qua tuổi thọ vũ trụ), giải thích lý do vì sao ransomware không thể bị giải mã nếu không có Private Key hoặc bản sao lưu.

---

## 📚 8. Khung tham chiếu chuẩn quốc tế

Đồ án được xây dựng bám sát các khung tiêu chuẩn an toàn thông tin hàng đầu:
* **MITRE ATT&CK Framework for Enterprise:**
  * `T1486`: Data Encrypted for Impact (Kỹ thuật mã hóa phá hoại mục tiêu).
  * `T1490`: Inhibit System Recovery (Xóa bản sao lưu phục hồi hệ thống).
  * `T1083`: File and Directory Discovery (Dò quét cấu trúc tệp tin).
* **NIST SP 800-61 Rev. 2:** Computer Security Incident Handling Guide (Quy trình 6 bước ứng phó sự cố an ninh mạng).
* **Cryptovirology Research:** Định lý mã hóa lai của Adam L. Young & Moti Yung (IEEE S&P).

---

<p align="center">
  <b>Tác giả:</b> Sinh viên môn An Ninh Mạng<br>
  <i>Bản quyền thuộc sở hữu cá nhân phục vụ học tập và nghiên cứu học thuật an toàn 100%.</i>
</p>

