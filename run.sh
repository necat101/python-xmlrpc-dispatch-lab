#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then PY=python; fi
"$PY" -m py_compile $(find . -name "*.py" -not -path "./.venv/*" 2>/dev/null) || true
"$PY" run_lab.py "$@"
