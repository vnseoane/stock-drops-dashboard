@echo off
setlocal
cd /d "%~dp0"
set PORT=8501
start "Streamlit - stock-drops-dashboard" "%cd%\.venv\Scripts\python.exe" -m streamlit run "%cd%\app\main.py" --server.port %PORT% --server.headless true
start "" http://localhost:%PORT%
