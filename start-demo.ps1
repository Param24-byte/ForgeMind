Write-Host "================================================="
Write-Host " Booting Unified Operations Brain Hackathon Demo "
Write-Host "================================================="

Write-Host "`n[1/2] Starting FastAPI Backend on port 8000..."
Start-Process powershell -ArgumentList "-NoExit -Command cd backend; if (Test-Path .venv\Scripts\activate.ps1) { .\.venv\Scripts\activate.ps1 } else { Write-Host 'Virtual env not found, attempting to run globally' }; uvicorn src.api.main:app --reload --port 8000"

Write-Host "[2/2] Starting Next.js Frontend on port 3000..."
Start-Process powershell -ArgumentList "-NoExit -Command cd frontend; npm run dev"

Write-Host "`nAll systems are booting! "
Write-Host "-> Backend: http://localhost:8000/docs (Swagger UI)"
Write-Host "-> Frontend: http://localhost:3000"
Write-Host "`nPlease wait ~10 seconds for Next.js to compile before opening the frontend."
