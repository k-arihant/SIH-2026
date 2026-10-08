@echo off
cd /d d:\desktop\Project\SIH mobile app\backend
C:\Python313\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
