@echo off
start "celery�첽����" cmd /k "f: && cd F:\Programming\Project\Donburi-main && call .\venv\Scripts\activate.bat && cd backend && celery -A Donburi worker --loglevel=info -P eventlet -c 10"

start "celery��������" cmd /k "f: && cd F:\Programming\Project\Donburi-main && call .\venv\Scripts\activate.bat && cd backend && celery -A Donburi beat --loglevel=info"