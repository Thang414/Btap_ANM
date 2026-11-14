@echo off
title Chay Kiem Thu Tu Dong - Ransomware Simulator
color 0B
cls

echo ===============================================================================
echo       CHAY BO KIEM THU TU DONG (AUTOMATED TEST SUITE)
echo       Do an: Mo phong Ransomware - Ma doc tong tien
echo ===============================================================================
echo.

python -m pytest -v

echo.
echo ===============================================================================
if %errorlevel% equ 0 (
    color 0A
    echo   [SUCCESS] TAT CA CAC CA KIEM THU (18/18 TESTS) DA DAT 100%%!
) else (
    color 0C
    echo   [FAILURE] CO CA KIEM THU KHONG DAT! VUI LONG KIEM TRA LOG O TREN.
)
echo ===============================================================================
pause
