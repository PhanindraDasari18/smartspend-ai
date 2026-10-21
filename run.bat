@echo off
setlocal
title SmartSpend AI
cd /d "%~dp0frontend"

where node.exe >nul 2>nul
if errorlevel 1 goto no_node
where npm.cmd >nul 2>nul
if errorlevel 1 goto no_npm

if not exist "node_modules\vite\bin\vite.js" (
  echo Installing the app the first time. This needs an internet connection...
  call npm.cmd install
  if errorlevel 1 goto install_failed
)

echo Starting SmartSpend AI in a separate window...
start "SmartSpend AI server" /D "%~dp0frontend" cmd /k npm.cmd run dev -- --host 127.0.0.1
timeout /t 3 /nobreak >nul
start "" http://localhost:5173
echo Choose Explore with demo data in the browser.
echo Keep the SmartSpend AI server window open while using the app.
timeout /t 5
exit /b

:no_node
echo Node.js is not installed or is not on PATH.
echo Install the Node.js LTS version from https://nodejs.org, then restart this computer and try again.
goto failed

:no_npm
echo npm was not found. Reinstall Node.js LTS and ensure npm is selected during setup.
goto failed

:install_failed
echo Dependency installation failed. Check your internet connection and try again.
goto failed

:failed
echo.
pause
exit /b 1
