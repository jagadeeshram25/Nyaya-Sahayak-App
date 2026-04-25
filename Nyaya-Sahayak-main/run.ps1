
Write-Host "==================================================="
Write-Host "     Nyaya-Sahayak - BNS Legal Assistant"
Write-Host "==================================================="
Write-Host ""
Write-Host "Starting Streamlit Application..."
Write-Host ""

$venvPython = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Error: .venv\Scripts\python.exe not found."
    Write-Host "Please reinstall the environment: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit
}

& $venvPython -m streamlit run ui/streamlit_app.py

Write-Host ""
Write-Host "Application stopped."
Read-Host "Press Enter to exit"
