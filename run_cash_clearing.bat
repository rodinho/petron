@echo off
setlocal
set PYTHON="C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe"
title Petron Cash Clearing Automation
echo ========================================================
echo          PETRON CASH CLEARING DROP AUTOMATION
echo ========================================================
echo.

if not "%~1"=="" goto WITH_ARGS

:INTERACTIVE
echo [Interactive Mode] Press Enter to run ALL dates, or enter a specific date:
set /p TARGET_DATE="Enter Date [e.g. 01, 01/09, 2026-09-01, or Enter for all]: "
echo.
set /p ACCEPTED_BY="Accepted by [press Enter for Owner hazieqaf98]: "
echo.
if "%TARGET_DATE%"=="" set TARGET_DATE=all
if "%ACCEPTED_BY%"=="" (
    %PYTHON% automate_cash_clearing.py "%TARGET_DATE%"
) else (
    %PYTHON% automate_cash_clearing.py "%TARGET_DATE%" "%ACCEPTED_BY%"
)
goto DONE

:WITH_ARGS
%PYTHON% automate_cash_clearing.py %*
goto DONE

:DONE
echo.
echo ========================================================
echo   Cash Clearing process completed!
echo ========================================================
pause
