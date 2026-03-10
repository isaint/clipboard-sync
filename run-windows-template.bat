@echo off
cd /d %~dp0
set SB_CONNECTION_STRING=__REPLACE_ME_CONNECTION_STRING__
set SB_QUEUE_NAME=clipboard-sync
set DEVICE_ID=win-sant
clipboard-sync.exe
