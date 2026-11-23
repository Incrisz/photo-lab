#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi

# Install only when dependencies are missing or their versions have changed.
if ! .venv/bin/python - <<'PY'
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
try:
    for line in Path("requirements.txt").read_text().splitlines():
        name, expected = line.split("==")
        if version(name) != expected:
            raise SystemExit(1)
except PackageNotFoundError:
    raise SystemExit(1)
PY
then
  .venv/bin/python -m pip install -r requirements.txt
fi

exec .venv/bin/python run.py
