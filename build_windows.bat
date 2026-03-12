@echo off
setlocal

echo [Rippler] Building Windows executable with PyInstaller...
pyinstaller --clean --noconfirm pyinstaller.spec

if errorlevel 1 (
  echo [Rippler] Build failed.
  exit /b 1
)

echo [Rippler] Build finished: dist\Rippler.exe
endlocal
