@echo off
echo =======================================================================
echo   SnapFlow AI - 1-Click Setup for Snapdragon HP PCs (Windows on ARM)
echo   Optimized for Qualcomm Hexagon NPU (45 TOPS)
echo =======================================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 64-bit from python.org or Microsoft Store.
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo [2/3] Installing optimized dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/3] Checking ONNX Runtime QNN Provider libraries...
python -c "import onnxruntime as ort; print('Available Providers:', ort.get_available_providers())"

echo.
echo =======================================================================
echo   Setup Complete! Launching SnapFlow AI Dashboard...
echo =======================================================================
python run_snapflow.py
pause
