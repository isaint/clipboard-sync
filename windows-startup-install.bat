@echo off
setlocal
set TARGET=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\clipboard-sync.bat
copy /Y "%~dp0run-windows.bat" "%TARGET%"
echo Installed to %TARGET%
