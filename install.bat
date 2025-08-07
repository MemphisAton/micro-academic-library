@echo off
py -3.12 -m venv .venv
".\.venv\Scripts\pip.exe" install wheel
".\.venv\Scripts\pip.exe" install -r requirements.txt
echo.
echo Dependencies installed successfully.
timeout 10
