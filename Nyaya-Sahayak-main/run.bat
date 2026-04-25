@echo off
echo ===================================================
echo      Nyaya-Sahayak - BNS Legal Assistant
echo ===================================================
echo.
echo Starting Streamlit Application using specific Python...
echo.

REM Check if python executable exists in .venv
if not exist ".venv\Scripts\python.exe" (
    echo Error: .venv\Scripts\python.exe not found.
    echo Please reinstall the environment: python -m venv .venv && .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b
)

REM Run directly with the venv python
".venv\Scripts\python.exe" -m streamlit run ui/streamlit_app.py

echo.
echo Application stopped.
pause
