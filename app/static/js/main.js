/**
 * Main JavaScript Library for Cyber SOC Dashboard
 * Project: Mô phỏng Ransomware – Mã độc tống tiền
 */

const CyberAPI = {
    async get(endpoint) {
        try {
            const res = await fetch(endpoint);
            return await res.json();
        } catch (err) {
            console.error(`API GET error on ${endpoint}:`, err);
            return { success: false, error: err.message };
        }
    },

    async post(endpoint, payload = {}) {
        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            return await res.json();
        } catch (err) {
            console.error(`API POST error on ${endpoint}:`, err);
            return { success: false, error: err.message };
        }
    }
};

// ================= Toast Notifications =================
function showToast(message, type = "success") {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `<strong>${type.toUpperCase()}:</strong> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ================= Global Sandbox Actions =================
async function triggerSandboxReset() {
    if (!confirm("XÁC NHẬN: Bạn có chắc chắn muốn đặt lại (Reset) toàn bộ thư mục Sandbox về trạng thái sạch ban đầu?")) {
        return;
    }

    showToast("Đang khôi phục thư mục Sandbox...", "info");
    const res = await CyberAPI.post("/api/sandbox/reset");

    if (res.success) {
        showToast("Đã Reset Sandbox thành công! Tất cả tệp mẫu đã được làm mới.", "success");
        if (window.reloadDashboard) {
            window.reloadDashboard();
        } else {
            setTimeout(() => window.location.reload(), 800);
        }
    } else {
        showToast(`Lỗi reset: ${res.error}`, "error");
    }
}

async function triggerQuickSnapshot() {
    showToast("Đang tạo bản chụp Snapshot sạch...", "info");
    const res = await CyberAPI.post("/api/defense/snapshot/create", { snapshot_name: "baseline_snapshot" });

    if (res.success) {
        showToast(`Tạo Snapshot thành công (${res.result.files_copied} tệp)!`, "success");
    } else {
        showToast(`Lỗi tạo snapshot: ${res.error}`, "error");
    }
}

async function triggerQuickRollback() {
    if (!confirm("Khôi phục toàn bộ tệp tin từ bản sao lưu sạch (Shadow Snapshot)?")) {
        return;
    }
    showToast("Đang phục hồi dữ liệu từ Snapshot...", "info");
    const res = await CyberAPI.post("/api/defense/snapshot/rollback", { snapshot_name: "baseline_snapshot" });

    if (res.success) {
        showToast(`Phục hồi thành công ${res.result.restored_files_count} tệp tin sạch!`, "success");
        if (window.reloadDashboard) {
            window.reloadDashboard();
        } else {
            setTimeout(() => window.location.reload(), 800);
        }
    } else {
        showToast(`Lỗi phục hồi: ${res.error}`, "error");
    }
}

// ================= Threat Banner Monitor =================
async function updateThreatBanner() {
    const res = await CyberAPI.get("/api/defense/canary-status");
    const banner = document.getElementById("threat-banner");
    const bannerText = document.getElementById("threat-banner-text");

    if (res.success && res.status.any_tripped) {
        if (banner) banner.classList.add("active");
        if (bannerText) {
            bannerText.innerText = "🚨 BÁO ĐỘNG ĐỎ: Phát hiện tệp mồi nhử Canary bị mã hóa/thay đổi! Nguy cơ Ransomware đang hoành hành.";
        }
    } else {
        if (banner) banner.classList.remove("active");
    }
}

// Check every 8 seconds
setInterval(updateThreatBanner, 8000);
document.addEventListener("DOMContentLoaded", updateThreatBanner);
