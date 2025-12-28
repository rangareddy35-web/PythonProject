#!/usr/bin/env powershell
param(
    [switch]$SkipVenv = $false
)

Set-Location "F:\anjali\PythonProject"

Write-Host "============================================================" -ForegroundColor Green
Write-Host "  APPOINTMENT BOOKING API - DEPENDENCY INSTALLATION" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

if (-not $SkipVenv) {
    # Remove old venv if exists
    if (Test-Path ".venv") {
        Write-Host "[1/4] Removing old virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force .venv
        Write-Host "✓ Old virtual environment removed" -ForegroundColor Green
    }

    # Create new venv
    Write-Host "[2/4] Creating virtual environment..." -ForegroundColor Yellow
    & python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }

    # Activate venv
    Write-Host "[3/4] Activating virtual environment..." -ForegroundColor Yellow
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
}

# Upgrade pip
Write-Host "[4/4] Upgrading pip, setuptools, and wheel..." -ForegroundColor Yellow
& python -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pip upgraded" -ForegroundColor Green
}

# Install requirements
Write-Host "[5/5] Installing project requirements..." -ForegroundColor Yellow
$reqFile = "requirements.txt"
if (Test-Path $reqFile) {
    & pip install -r $reqFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Requirements installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install requirements" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ requirements.txt not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  ✓ Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure .env file (copy from .env.example if needed)"
Write-Host "2. Start PostgreSQL: docker-compose up -d"
Write-Host "3. Initialize database: python -m scripts.setup_db"
Write-Host "4. Run the app: python main.py"
Write-Host "5. Visit API docs: http://localhost:8000/docs"
Write-Host ""

