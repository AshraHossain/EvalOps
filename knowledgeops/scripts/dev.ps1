param([string]$Command = "help")

$BackendDir = "$PSScriptRoot\..\backend"

switch ($Command) {
    "run" {
        Write-Host "Starting KnowledgeOps API on :8100..."
        Set-Location $BackendDir
        if (-not (Test-Path ".venv")) { python -m venv .venv }
        & .venv\Scripts\activate.ps1
        pip install -r requirements.txt -q
        uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload --loop asyncio
    }
    "test" {
        Write-Host "Running tests..."
        Set-Location $BackendDir
        & .venv\Scripts\activate.ps1
        pytest tests/ -v
    }
    "up" {
        Write-Host "Starting KnowledgeOps container..."
        docker compose -f "$PSScriptRoot\..\docker-compose.yml" up -d --build
    }
    "down" {
        docker compose -f "$PSScriptRoot\..\docker-compose.yml" down
    }
    default {
        Write-Host "Usage: dev.ps1 [run|test|up|down]"
    }
}
