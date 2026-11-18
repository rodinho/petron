@echo off
setlocal
set PYTHON="C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe"
title Petron EOD Automatic Document Uploader
echo ========================================================
echo       PETRON EOD AUTOMATIC DOCUMENT UPLOADER
echo   [Auto-Read: ON - Triggers Read files after each day]
echo ========================================================
echo.

if not "%~1"=="" goto WITH_ARGS

:INTERACTIVE
echo [Interactive Mode] Press Enter to run ALL, or enter specific filters:
set /p TARGET_DATE="1. Enter Date [e.g. 02, 09-30, 02/09, 2026-09-02, Enter for all]: "
set /p TARGET_POS="2. Enter POS or Slot [e.g. pos1, pos2, pos3, opt, der, Enter for all]: "
echo.
if not "%TARGET_DATE%"=="" (
    if not "%TARGET_POS%"=="" (
        %PYTHON% upload_all_eod.py "%TARGET_DATE%" "%TARGET_POS%"
    ) else (
        %PYTHON% upload_all_eod.py "%TARGET_DATE%"
    )
) else (
    if not "%TARGET_POS%"=="" (
        %PYTHON% upload_all_eod.py all "%TARGET_POS%"
    ) else (
        %PYTHON% upload_all_eod.py
    )
)
goto DONE

:WITH_ARGS
%PYTHON% upload_all_eod.py %*
goto DONE

:DONE
echo.
echo ========================================================
echo   Process completed!
echo ========================================================
pause
