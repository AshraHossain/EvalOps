param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("up", "migrate", "run", "test")]
    [string]$Command
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"

function Invoke-Checked {
    param([ScriptBlock]$Action)
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE."
    }
}

switch ($Command) {
    "up" {
        Invoke-Checked { docker-compose -f (Join-Path $repoRoot "infrastructure/docker/docker-compose.yml") up -d }
    }
    "migrate" {
        Push-Location $backendDir
        try {
            Invoke-Checked { .\.venv\Scripts\python -m alembic upgrade head }
        }
        finally {
            Pop-Location
        }
    }
    "run" {
        Push-Location $backendDir
        try {
            Invoke-Checked { .\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000 --loop asyncio }
        }
        finally {
            Pop-Location
        }
    }
    "test" {
        Push-Location $backendDir
        try {
            Invoke-Checked { .\.venv\Scripts\python -m pytest -q }
        }
        finally {
            Pop-Location
        }
    }
}
