$ErrorActionPreference = "Stop"

Write-Host "Setting up the demo..." -ForegroundColor Cyan

# 1. Start Redis
Write-Host "[1/4] Starting Redis container..." -ForegroundColor Yellow
docker compose up -d redis
if ($LASTEXITCODE -ne 0) {
    Write-Host "Could not start Redis. Please check if Docker is running." -ForegroundColor Red
    exit 1
}

# 2. Generate baseline data and train models
Write-Host "[2/4] Generating baseline data and training models..." -ForegroundColor Yellow
uv run python src/scripts/generate_baseline.py

# 3. Start the API
Write-Host "[3/4] Starting FastAPI backend in a new window..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000"

# Wait a couple seconds to ensure API is up before Streamlit tries to connect
Start-Sleep -Seconds 3

# 4. Start the Dashboard
Write-Host "[4/4] Starting Streamlit dashboard in a new window..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uv run streamlit run src/ui/app.py"

Write-Host ""
Write-Host "Done. The environment is running." -ForegroundColor Green
Write-Host "The dashboard will open in your browser at http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "To run the demo scenario, run:" -ForegroundColor Cyan
Write-Host "  uv run python src/scripts/run_demo.py" -ForegroundColor White
Write-Host ""
