@echo off
REM ============================================================
REM  INDUS CROPWISE AI - Windows launcher
REM  Team INDUSASTRA | NASA Space Apps 2026 | Field Shift
REM ============================================================
cd /d "%~dp0"

echo [1/3] Creating virtual environment (first run only)...
if not exist ".venv" (
    python -m venv .venv
)

echo [2/3] Installing requirements...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt

echo [3/3] Launching Indus CropWise AI...
echo The app will open in your browser at http://localhost:8501
streamlit run app.py

pause
