#!/usr/bin/env zsh
set -euo pipefail
cd "${0:A:h}"
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then PY=python; fi
"$PY" -m py_compile $(find . -name "*.py" -not -path "./.venv/*" 2>/dev/null)
"$PY" run_lab.py "$@"
