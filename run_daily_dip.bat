@echo off
set PYTHON="C:\Users\User\AppData\Local\Programs\Python\Python310\python.exe"
echo ========================================================
echo       PETRON ACTUAL DAILY DIP AUTOMATION TOOL
echo ========================================================
echo Running automated Daily Dip input for Grand Saga Northbound...
%PYTHON% automate_daily_dip.py %1
pause
