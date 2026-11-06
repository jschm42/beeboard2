# ==============================================================================
# BeeBoard 2 - Windows PowerShell Setup Script
# ==============================================================================
# Dieses Skript richtet das Backend unter Windows mit Poetry ein (virtuelle Umgebung backend/.venv),
# installiert alle Abhaengigkeiten und konfiguriert die .env-Datei.
# ==============================================================================

# Verzeichnisse ermitteln
$ScriptDir = $PSScriptRoot
if ([string]::IsNullOrEmpty($ScriptDir)) { $ScriptDir = Get-Location }
$RootDir = Split-Path -Path $ScriptDir -Parent
$BackendDir = Join-Path -Path $RootDir -ChildPath "backend"

Write-Host "====================================================================" -ForegroundColor Blue
Write-Host "BeeBoard 2 - Automatisches Windows Setup & Konfiguration" -ForegroundColor Blue
Write-Host "====================================================================" -ForegroundColor Blue
Write-Host ""

# 1. Python-Installation ueberpruefen
Write-Host "[1] Schritt 1: Python-Installation ueberpruefen..." -ForegroundColor Blue
$pythonCmd = $null

if (Get-Command "python3" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
}

if ($null -eq $pythonCmd) {
    Write-Host "[-] Fehler: Python wurde nicht gefunden!" -ForegroundColor Red
    Write-Host "Bitte installieren Sie Python 3.12+ (Python 3.13 empfohlen) von https://www.python.org/ und versuchen Sie es erneut."
    Write-Host "Stellen Sie sicher, dass bei der Installation 'Add Python to PATH' ausgewaehlt ist."
    Exit 1
}

$pyVersion = & $pythonCmd --version
Write-Host "[+] Python gefunden: $pyVersion (Kommando: $pythonCmd)" -ForegroundColor Green
Write-Host ""

# 2. Poetry-Installation ueberpruefen
Write-Host "[2] Schritt 2: Poetry-Installation ueberpruefen..." -ForegroundColor Blue
if (-not (Get-Command "poetry" -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Poetry wurde nicht gefunden." -ForegroundColor Yellow
    $installPoetry = Read-Host "Soll Poetry jetzt per pip (--user) installiert werden? (Y/n)"
    if ($installPoetry -match "^[Nn]$") {
        Write-Host "[-] Poetry wird benoetigt: https://python-poetry.org/docs/#installation" -ForegroundColor Red
        Exit 1
    }
    & $pythonCmd -m pip install --user "poetry>=2.0.0,<3.0.0"
    if (-not (Get-Command "poetry" -ErrorAction SilentlyContinue)) {
        Write-Host "[-] Poetry wurde installiert, ist aber nicht im PATH. Bitte PATH ergaenzen und Skript erneut starten." -ForegroundColor Red
        Exit 1
    }
}
$poetryVersion = & poetry --version
Write-Host "[+] Poetry gefunden: $poetryVersion" -ForegroundColor Green
Write-Host ""

# 3. Abhaengigkeiten mit Poetry installieren (virtuelle Umgebung: backend/.venv, siehe backend/poetry.toml)
Write-Host "[3] Schritt 3: Abhaengigkeiten mit Poetry installieren..." -ForegroundColor Blue
$venvPath = Join-Path -Path $BackendDir -ChildPath ".venv"

if (Test-Path -Path $venvPath) {
    Write-Host "[!] Eine virtuelle Umgebung existiert bereits unter backend/.venv." -ForegroundColor Yellow
    $recreate = Read-Host "Moechten Sie diese loeschen und neu erstellen? (y/N)"
    if ($recreate -match "^[Yy]$") {
        Write-Host "Loesche alte Umgebung..."
        Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "Bestehende Umgebung wird beibehalten."
    }
}

Push-Location $BackendDir
try {
    & poetry env use $pythonCmd | Out-Null
    Write-Host "Installiere Pakete mit Poetry (dies kann einen Moment dauern)..."
    & poetry install --no-interaction
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[-] Fehler: poetry install ist fehlgeschlagen." -ForegroundColor Red
        Exit 1
    }
    $venvPython = (& poetry env info --executable).Trim()
} finally {
    Pop-Location
}
Write-Host "[+] Abhaengigkeiten erfolgreich installiert." -ForegroundColor Green
Write-Host ""

# 4. .env Datei anlegen und konfigurieren
Write-Host "[4] Schritt 4: Umgebungsvariablen konfigurieren..." -ForegroundColor Blue
$envExamplePath = Join-Path -Path $RootDir -ChildPath ".env.example"
$envPath = Join-Path -Path $RootDir -ChildPath ".env"

$generateKey = $true
if (Test-Path -Path $envPath) {
    Write-Host "[!] Eine .env Datei existiert bereits im Hauptverzeichnis." -ForegroundColor Yellow
    $overwrite = Read-Host "Moechten Sie diese mit der .env.example ueberschreiben? (y/N)"
    if ($overwrite -match "^[Yy]$") {
        Copy-Item -Path $envExamplePath -Destination $envPath -Force
        $generateKey = $true
    } else {
        Write-Host "Bestehende .env Datei wird beibehalten."
        $generateKey = $false
    }
} else {
    Copy-Item -Path $envExamplePath -Destination $envPath
    Write-Host "[+] .env.example wurde nach .env kopiert." -ForegroundColor Green
    $generateKey = $true
}

if ($generateKey) {
    Write-Host "Generiere sicheren SECRET_KEY..."
    $randomSecret = & $venvPython -c "import secrets; print(secrets.token_hex(32))"
    
    # Text-Ersetzung und Speicherung als UTF-8
    $content = [System.IO.File]::ReadAllText($envPath, [System.Text.Encoding]::UTF8)
    $content = $content.Replace('SECRET_KEY="supersecretkeychangeinproduction1234567890"', "SECRET_KEY=""$randomSecret""")
    [System.IO.File]::WriteAllText($envPath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "[+] Zufaelliger SECRET_KEY wurde in der zentralen .env eingetragen." -ForegroundColor Green
}

# Abfrage des Gemini API Keys
$hasEmptyKey = $false
if (Test-Path -Path $envPath) {
    $content = [System.IO.File]::ReadAllText($envPath, [System.Text.Encoding]::UTF8)
    if ($content.Contains('GEMINI_API_KEY=""')) {
        $hasEmptyKey = $true
    }
}

if ($generateKey -or $hasEmptyKey) {
    Write-Host ""
    Write-Host "[AI] KI-Integration einrichten:" -ForegroundColor Blue
    Write-Host "Wenn Sie die KI-Features und den Stockkarten-Entwurf nutzen moechten,"
    Write-Host "koennen Sie hier Ihren Google Gemini API Key eingeben."
    Write-Host "Diesen erhalten Sie kostenlos unter: https://aistudio.google.com/"
    $geminiKey = Read-Host "Gemini API Key eingeben (oder [Enter] zum Ueberspringen)"
    
    if (-not [string]::IsNullOrEmpty($geminiKey)) {
        $content = [System.IO.File]::ReadAllText($envPath, [System.Text.Encoding]::UTF8)
        $content = $content.Replace('GEMINI_API_KEY=""', "GEMINI_API_KEY=""$geminiKey""")
        [System.IO.File]::WriteAllText($envPath, $content, [System.Text.Encoding]::UTF8)
        Write-Host "[+] GEMINI_API_KEY wurde in der zentralen .env gespeichert." -ForegroundColor Green
    } else {
        Write-Host "[!] Uebersprungen. Sie koennen den GEMINI_API_KEY spaeter manuell in der .env eintragen." -ForegroundColor Yellow
    }
}
Write-Host ""

# Ports auslesen fuer die Anleitung am Ende
$finalBackendPort = 8000
$finalFrontendPort = 3200
if (Test-Path -Path $envPath) {
    $envLines = Get-Content $envPath | Where-Object { $_ -match "^#" -eq $false -and $_ -match "=" }
    foreach ($line in $envLines) {
        $parts = $line -split "=", 2
        if ($parts.Length -eq 2) {
            $key = $parts[0].Trim().Trim('"')
            $value = $parts[1].Trim().Trim('"')
            if ($key -eq "BEEBOARD_BACKEND_PORT") { $finalBackendPort = [int]$value }
            if ($key -eq "BEEBOARD_FRONTEND_PORT") { $finalFrontendPort = [int]$value }
        }
    }
}

# 5. Abschluss und Anleitung
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "[+] Setup erfolgreich abgeschlossen!" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Gehen Sie wie folgt vor, um BeeBoard 2 zu starten:"
Write-Host ""
Write-Host "1. Backend-Datenbank initialisieren & starten:" -ForegroundColor Blue
Write-Host "   cd backend"
Write-Host "   # Datenbank-Migrationen anwenden:"
Write-Host "   poetry run alembic upgrade head"
Write-Host "   # Datenbank mit Standard-Daten befuellen:"
Write-Host "   poetry run python -m app.scripts.seed"
Write-Host "   # Server starten:"
Write-Host "   poetry run uvicorn app.main:app --reload --port $finalBackendPort"
Write-Host ""
Write-Host "2. Frontend installieren & starten:" -ForegroundColor Blue
Write-Host "   cd frontend"
Write-Host "   npm install"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "Viel Spass mit BeeBoard 2! :)"
