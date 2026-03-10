param(
  [string]$Entry = ".\clipboard_sync.py"
)

$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install pyinstaller -r .\requirements.txt

pyinstaller \
  --noconfirm \
  --clean \
  --onefile \
  --name clipboard-sync \
  $Entry

Write-Host "Built: .\dist\clipboard-sync.exe"
