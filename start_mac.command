#!/bin/bash
# ===================================================================
#  E-Commerce AI Team - Mac / Linux launcher
#  DOUBLE-CLICK this file (Mac) or run ./start_mac.command
#  First time on Mac: right-click -> Open (to allow it).
# ===================================================================
cd "$(dirname "$0")"

echo ""
echo "  Starting your E-Commerce AI Team..."
echo "  (First time may take a minute to install helpers.)"
echo ""

# find python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "  Python was not found. Install it from https://python.org/downloads then run again."
  read -r -p "  Press Enter to close..."
  exit 1
fi

$PY -m pip install -q -r requirements.txt
$PY web.py

echo ""
echo "  The app has stopped. You can close this window."
read -r -p "  Press Enter to close..."
