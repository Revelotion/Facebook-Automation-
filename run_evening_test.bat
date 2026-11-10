@echo off
cd /d "%~dp0"
python post.py --slot evening --dry-run
pause
