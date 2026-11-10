@echo off
cd /d "%~dp0"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env
if not exist config.json copy config.example.json config.json
echo.
echo Dependencies installed. Now edit .env and configure config.json or run get_token.py.
pause
