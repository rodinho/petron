@echo off
setlocal
set PYTHON="C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe"
title Petron Fuel Deliveries Automation
echo ========================================================
echo       PETRON FUEL DELIVERIES INVOICE AUTOMATION
echo ========================================================
echo.

if "%~1"=="" (
    echo [Interactive Mode] Press Enter to upload ALL fuel invoices, or enter specific invoice:
    set /p TARGET_INV="Enter Invoice name/number (e.g. IN9018213197, or press Enter for all): "
    echo.
    if not "%TARGET_INV%"=="" (
        %PYTHON% automate_fuel_deliveries.py "%TARGET_INV%"
    ) else (
        %PYTHON% automate_fuel_deliveries.py
    )
) else (
    %PYTHON% automate_fuel_deliveries.py %*
)

echo.
echo ========================================================
echo   Process completed! Open Petron Fuel Deliveries page.
echo ========================================================
pause
