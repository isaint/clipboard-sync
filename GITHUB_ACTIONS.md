# GitHub Actions Build

## Purpose

Automatically build:
- Windows: `clipboard-sync.exe`
- macOS: `clipboard-sync`

without requiring you to have a local Windows build environment.

## Files

- `.github/workflows/build.yml`

## How to use

1. Put `clipboard-sync/` into a GitHub repository
2. Push to GitHub
3. Open **Actions** tab
4. Run `build-clipboard-sync` manually, or let push trigger it
5. Download artifacts:
   - `clipboard-sync-windows`
   - `clipboard-sync-macos`

## What artifacts contain

### Windows artifact

- `clipboard-sync.exe`
- `run-windows.bat`
- `windows-startup-install.bat`
- `README.md`
- `PACKAGING.md`

### macOS artifact

- `clipboard-sync`
- `run-macos.sh`
- `com.sant.clipboard-sync.plist`
- `README.md`
- `PACKAGING.md`

## Important security note

The workflow intentionally does **not** inject your Service Bus connection string into the generated files.

Why:
- avoids leaking secrets into artifacts
- avoids accidentally committing admin-level connection strings
- lets you set different keys per device

## Recommended final step

After downloading artifacts:

- edit `run-windows.bat` / `run-macos.sh`
- fill in:
  - `SB_CONNECTION_STRING`
  - `SB_QUEUE_NAME`
  - `DEVICE_ID`

Then distribute only to your own machines.
