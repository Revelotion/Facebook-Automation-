@echo off
cd /d "%~dp0"
python post.py --slot morning --dry-run
pause
