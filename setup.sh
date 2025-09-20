#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "\nVirtual environment ready. To start developing, run:"
echo "source .venv/bin/activate"
echo "streamlit run app_hello.py"
