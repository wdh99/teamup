@echo off
CWD = %~dp0
start "django" cmd /k "f: && cd %CWD% && call .\venv\Scripts\activate.bat && cd teamup && python manage.py runserver 0.0.0.0:8000"