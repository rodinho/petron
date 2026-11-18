@echo off
setlocal
set PYTHON="C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe"
set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
title Petron OPT File Automatic Uploader (08 to 30)

echo ========================================================
echo       PETRON OPT DOCUMENT AUTOMATIC UPLOADER
echo       Target: Folders 08 to 30 (September 2026)
echo ========================================================
echo.
echo Launching Google Chrome for Google Sign-in...
start "" %CHROME% --remote-debugging-port=9222 --user-data-dir="%~dp0browser_profile" "https://petron.myhiro.my/station/eod?date=2026-09-08"

echo.
echo ========================================================
echo  INSTRUCTIONS:
echo  1. In the Chrome window, sign in using your Google account.
echo  2. Once signed in and you see the Dealer Dashboard,
echo     come back here and press any key to start uploading!
echo ========================================================
echo.
pause

%PYTHON% upload_opt_files.py --cdp 9222 --start 8 --end 30 --month 09 --year 2026

echo.
echo ========================================================
echo   Process completed! All OPT files have been processed.
echo ========================================================
pause
