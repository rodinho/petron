@echo off
setlocal
set PYTHON="C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe"
title Petron Sales Clearing Till Automation
echo ========================================================
echo       PETRON SALES CLEARING TILL AUTOMATION
echo ========================================================
echo.

if not "%~1"=="" goto WITH_ARGS

:INTERACTIVE
echo [Interactive Mode] Press Enter to run ALL dates, or enter a specific date:
set /p TARGET_DATE="Enter Date [e.g. 01, 01/09, 2026-09-01, or Enter for all]: "
echo.
if "%TARGET_DATE%"=="" (
    %PYTHON% automate_sales_clearing.py all
) else (
    %PYTHON% automate_sales_clearing.py "%TARGET_DATE%"
)
goto DONE

:WITH_ARGS
%PYTHON% automate_sales_clearing.py %*
goto DONE

:DONE
echo.
echo ========================================================
echo   Sales Clearing process completed!
echo ========================================================
pause
