Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "  SnapFlow AI - PowerShell Setup for Snapdragon HP PCs (Windows on ARM)" -ForegroundColor Cyan
Write-Host "  Target: Qualcomm Hexagon NPU (45 TOPS) & HP OmniBook Ultra" -ForegroundColor Cyan
Write-Host "=======================================================================" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python was not found in your PATH." -ForegroundColor Red
    Exit 1
}

Write-Host "`n[1/3] Setting up Python virtual environment..." -ForegroundColor Yellow
python -m venv venv
& .\venv\Scripts\Activate.ps1

Write-Host "`n[2/3] Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "`n[3/3] Inspecting execution providers..." -ForegroundColor Yellow
python -c "import onnxruntime as ort; print('Available Providers:', ort.get_available_providers())"

Write-Host "`n=======================================================================" -ForegroundColor Green
Write-Host "  Setup Complete! Launching SnapFlow..." -ForegroundColor Green
Write-Host "=======================================================================" -ForegroundColor Green
python run_snapflow.py
