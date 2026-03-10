#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller -r requirements.txt

pyinstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name clipboard-sync \
  clipboard_sync.py

echo "Built: ./dist/clipboard-sync"
