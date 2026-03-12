@echo off
setlocal

cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe

"%PYTHON%" -m pip install -r requirements.txt

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q main.spec 2>nul

"%PYTHON%" -m PyInstaller ^
  --noconfirm ^
  --noconsole ^
  --clean ^
  --name "rippler" ^
  --onefile ^
  --icon "assets\icon.ico" ^
  --add-data "assets\*.*;." ^
  main.py

echo.
echo ==========================
echo   PyInstaller build done
echo   dist\rippler.exe
echo ==========================
echo.

pause