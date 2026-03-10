#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export SB_CONNECTION_STRING='__REPLACE_ME_CONNECTION_STRING__'
export SB_QUEUE_NAME='clipboard-sync'
export DEVICE_ID='macbook-sant'
./clipboard-sync
