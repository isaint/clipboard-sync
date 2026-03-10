@echo off
cd /d %~dp0
set SB_CONNECTION_STRING=YOUR_CONNECTION_STRING
set SB_QUEUE_NAME=clipboard-sync
set DEVICE_ID=win-sant
python clipboard_sync.py
