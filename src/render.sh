#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export DISPLAY=:93
export ITERATION="${1:-1}"
exec /home/dev/.local/opt/blender-4.2.3-linux-x64/blender -b --factory-startup --python-exit-code 1 -t 8 --python src/build_character.py
