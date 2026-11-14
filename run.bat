@echo off
title Mo phong Ransomware - Ma doc tong tien [ANM LAB]
color 0A
cls

echo ===============================================================================
echo       DO AN MON HOC: AN NINH MANG / AN TOAN THONG TIN
echo       DE TAI: MO PHONG RANSOMWARE - MA DOC TONG TIEN
echo       Attack ^& Defense Interactive Simulator (100%% Local Sandbox)
echo ===============================================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python chua duoc cai dat hoac chua duoc them vao PATH!
    echo Vui long cai dat Python 3.10 tro len tai https://www.python.org/
    pause
    exit /b 1
)

:: Install / Verify dependencies
echo [+] Kiem tra thu vien phu thuoc (requirements.txt)...
pip install -r requirements.txt --quiet

echo.
echo [+] Dang khoi chay Flask Web Application...
echo [+] Truy cap trinh duyet tai: http://127.0.0.1:5000
echo [+] Nhan Ctrl + C de dung may chu.
echo ===============================================================================
echo.

python run.py
pause

