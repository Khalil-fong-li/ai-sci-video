@echo off
rem ============================================================
rem  ai-sci-video  -  installer (Windows)
rem  Detects every agent skill folder on this machine and
rem  installs the skill into all of them. Double-click to run.
rem ============================================================
setlocal
set SRC=%~dp0

echo ============================================
echo   ai-sci-video installer
echo   From: %SRC%
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 goto NOPY

python "%SRC%install.py"
echo.
pause
exit /b 0

:NOPY
echo Python not found in PATH. Falling back to shared folder.
set DEST=%USERPROFILE%\.agents\skills\ai-sci-video
if not exist "%USERPROFILE%\.agents\skills" mkdir "%USERPROFILE%\.agents\skills"
xcopy /E /I /Y "%SRC%" "%DEST%\" >nul
if errorlevel 1 (
  echo [ERROR] Install failed.
  pause
  exit /b 1
)
echo [OK] Installed to %DEST%
echo Restart your agent session to load the skill.
pause
