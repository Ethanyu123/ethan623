@echo off
echo Starting FastAPI server...
uvicorn app:app --reload
pause
