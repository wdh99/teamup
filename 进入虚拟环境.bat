@echo off
CWD = %~dp0
start "venv" cmd /k "f: && cd %CWD% && call .\venv\Scripts\activate.bat && cd teamup"