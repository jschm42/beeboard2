param(
    [int]$HttpPort,
    [int]$HttpsPort,
    [int]$BackendPort,
    [string]$DataDir
)

# Fallback auf Werte aus .env, falls Parameter nicht gesetzt sind
$rootDir = Split-Path $PSScriptRoot -Parent
$backendEnvPath = Join-Path $rootDir ".env"
if (-not (Test-Path $backendEnvPath)) {
    $backendEnvPath = Join-Path $rootDir "backend\.env"
}
if (Test-Path $backendEnvPath) {
    $envLines = Get-Content $backendEnvPath | Where-Object { $_ -match "^#" -eq $false -and $_ -match "=" }
    foreach ($line in $envLines) {
        $parts = $line -split "=", 2
        if ($parts.Length -eq 2) {
            $key = $parts[0].Trim().Trim('"')
            $value = $parts[1].Trim().Trim('"')
            switch ($key) {
                "BEEBOARD_HTTP_PORT" { if (-not $HttpPort) { $HttpPort = [int]$value } }
                "BEEBOARD_HTTPS_PORT" { if (-not $HttpsPort) { $HttpsPort = [int]$value } }
                "BEEBOARD_BACKEND_PORT" { if (-not $BackendPort) { $BackendPort = [int]$value } }
                "BEEBOARD_DOCKER_DATA" { if (-not $DataDir) { $DataDir = $value } }
            }
        }
    }
}

if (-not $HttpPort) { $HttpPort = 8080 }
if (-not $HttpsPort) { $HttpsPort = 8443 }
if (-not $BackendPort) { $BackendPort = 8000 }
if (-not $DataDir) { $DataDir = "~/.beeboard2" }

# Expand ~ to USERPROFILE
if ($DataDir -like "~*") {
    $DataDir = $DataDir -replace "^~", $env:USERPROFILE
}

# Resolve to absolute path
$DataDir = [System.IO.Path]::GetFullPath($DataDir)

# Ensure the directory exists on the host with correct permissions
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
}

$env:BEEBOARD_HTTP_PORT = $HttpPort
$env:BEEBOARD_HTTPS_PORT = $HttpsPort
$env:BEEBOARD_BACKEND_PORT = $BackendPort
$env:BEEBOARD_DOCKER_DATA = $DataDir

# Sicherstellen, dass das certs-Verzeichnis existiert, damit das Volume gemountet werden kann
$certsDir = Join-Path $PSScriptRoot "certs"
if (-not (Test-Path $certsDir)) {
    New-Item -ItemType Directory -Path $certsDir -Force | Out-Null
}

Write-Host ""
Write-Host "Starte BeeBoard2 Unified Docker Stack mit:" -ForegroundColor Cyan
Write-Host "  HTTP Port:        $HttpPort" -ForegroundColor Cyan
Write-Host "  HTTPS Port:       $HttpsPort" -ForegroundColor Cyan
Write-Host "  Datenverzeichnis: $DataDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "SSL-Zertifikate werden bei Bedarf automatisch im Container generiert und in 'docker/certs/' gespeichert." -ForegroundColor Green
Write-Host ""

Write-Host "Updating repository from git..." -ForegroundColor Cyan
try {
    git -C $rootDir pull
} catch {
    Write-Host "Warning: git pull failed, building with current local files." -ForegroundColor Yellow
}

Push-Location $PSScriptRoot
try {
    docker compose -f .\docker-compose.yml up -d --build
} finally {
    Pop-Location
}
