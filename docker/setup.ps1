param(
    [int]$HttpPort,
    [int]$BackendPort,
    [string]$DataDir
)

# Fallback auf Werte aus backend/.env, falls Parameter nicht gesetzt sind
$backendEnvPath = Join-Path (Split-Path $PSScriptRoot -Parent) "backend\.env"
if (Test-Path $backendEnvPath) {
    $envLines = Get-Content $backendEnvPath | Where-Object { $_ -match "^#" -eq $false -and $_ -match "=" }
    foreach ($line in $envLines) {
        $parts = $line -split "=", 2
        if ($parts.Length -eq 2) {
            $key = $parts[0].Trim().Trim('"')
            $value = $parts[1].Trim().Trim('"')
            switch ($key) {
                "BEEBOARD_HTTP_PORT" { if (-not $HttpPort) { $HttpPort = [int]$value } }
                "BEEBOARD_BACKEND_PORT" { if (-not $BackendPort) { $BackendPort = [int]$value } }
                "BEEBOARD_DOCKER_DATA" { if (-not $DataDir) { $DataDir = $value } }
            }
        }
    }
}

if (-not $HttpPort) { $HttpPort = 8080 }
if (-not $BackendPort) { $BackendPort = 8000 }
if (-not $DataDir) { $DataDir = "data" }

$env:BEEBOARD_HTTP_PORT = $HttpPort
$env:BEEBOARD_BACKEND_PORT = $BackendPort
$env:BEEBOARD_DOCKER_DATA = $DataDir

Write-Host "Starting BeeBoard2 stack with:" -ForegroundColor Cyan
Write-Host "  HTTP Port:      $HttpPort" -ForegroundColor Cyan
Write-Host "  Backend Port:   $BackendPort" -ForegroundColor Cyan
Write-Host "  Data directory: $DataDir" -ForegroundColor Cyan

Push-Location $PSScriptRoot
try {
    docker compose -f .\docker-compose.yml up -d --build
} finally {
    Pop-Location
}
