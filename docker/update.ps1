param(
    [int]$HttpPort,
    [int]$HttpsPort,
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
Write-Host "Aktualisiere BeeBoard2 Unified Docker Stack (Rebuild + Restart)..." -ForegroundColor Cyan
Write-Host ""

Push-Location $PSScriptRoot
try {
    docker compose -f .\docker-compose.yml pull
    docker compose -f .\docker-compose.yml up -d --build
} finally {
    Pop-Location
}
