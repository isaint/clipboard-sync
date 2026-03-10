#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export SB_CONNECTION_STRING='YOUR_CONNECTION_STRING'
export SB_QUEUE_NAME='clipboard-sync'
export DEVICE_ID='macbook-sant'
python3 clipboard_sync.py
