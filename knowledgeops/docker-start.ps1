Write-Host "🚀 Starting KnowledgeOps Docker Stack..."
Write-Host "  Backend API: localhost:8100"
Write-Host ""

# Check if EvalOps is running
$evalopsRunning = docker ps --quiet --filter "name=evalops" 2>$null | Measure-Object -Line | Select-Object -ExpandProperty Lines
if ($evalopsRunning -eq 0) {
    Write-Host "⚠️  EvalOps is not running. Starting it first..."
    Push-Location ..\evalops\infrastructure\docker
    docker-compose up -d
    Pop-Location
    Start-Sleep -Seconds 5
}

docker-compose up -d

Write-Host "✓ Stack started!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Visit API docs: http://localhost:8100/docs"
Write-Host "  2. Try a query:"
Write-Host "     curl -X POST http://localhost:8100/api/v1/query \"
Write-Host "       -H 'Content-Type: application/json' \"
Write-Host "       -d '{""question"": ""What is AI?""}'"
Write-Host ""
Write-Host "To stop: docker-compose down"
