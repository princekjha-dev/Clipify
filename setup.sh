#!/usr/bin/env bash
set -e

printf "Creating Python virtual environment...\n"
python3 -m venv .venv

printf "Activating virtual environment and installing requirements...\n"
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

printf "Setup complete. Activate the environment with: source .venv/bin/activate\n"