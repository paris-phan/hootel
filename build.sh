#!/bin/bash
set -euo pipefail
echo "Installing dependencies..."
python -m pip install -r requirements.txt
# No migrations here (prefer a manual/CI step against your prod DB).
# No collectstatic here if static is on Blob already.
