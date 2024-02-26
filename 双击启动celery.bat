@echo off
start "celery异步任务" cmd /k "f: && cd F:\Programming\Project\Donburi-main && call .\venv\Scripts\activate.bat && cd backend && celery -A Donburi worker --loglevel=info -P eventlet -c 10"

start "celery周期任务" cmd /k "f: && cd F:\Programming\Project\Donburi-main && call .\venv\Scripts\activate.bat && cd backend && celery -A Donburi beat --loglevel=info"