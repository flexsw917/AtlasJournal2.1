python -m venv .venv
. .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "`nVirtual environment ready. To start developing, run:" 
Write-Host ".\\.venv\\Scripts\\Activate.ps1"
Write-Host "streamlit run app_hello.py"
