@echo off
cd /d "%~dp0.."
set PYTHONPATH=backend
set SUPABASE_URL=https://jbmqyxhrmcbdgardamrp.supabase.co
".venv\Scripts\python.exe" -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
