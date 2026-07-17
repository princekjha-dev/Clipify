@echo off
setlocal enabledelayedexpansion

echo Creating Python virtual environment...
python -m venv .venv

echo Activating virtual environment and installing requirements...
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete. To activate the environment later, run:
	echo .venv\Scripts\activate