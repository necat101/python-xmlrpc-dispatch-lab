@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (
  python run_lab.py %*
  exit /b %errorlevel%
)
echo python not found in PATH
exit /b 1
