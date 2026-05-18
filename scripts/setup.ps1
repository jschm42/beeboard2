# ==============================================================================
# 🐝 BeeBoard 2 — Windows PowerShell Setup Script
# ==============================================================================
# Dieses Skript richtet die virtuelle Umgebung (.venv) für das Backend unter Windows ein,
# installiert alle Abhängigkeiten und konfiguriert die .env-Datei.
# ==============================================================================

# UTF-8 Ausgabe erzwingen
$OutputEncoding = [System.Text.Encoding]::UTF8

# Verzeichnisse ermitteln
$ScriptDir = $PSScriptRoot
if ([string]::IsNullOrEmpty($ScriptDir)) { $ScriptDir = Get-Location }
$RootDir = Split-Path -Path $ScriptDir -Parent
$BackendDir = Join-Path -Path $RootDir -ChildPath "backend"

Write-Host "====================================================================" -ForegroundColor Blue
Write-Host "🐝 BeeBoard 2 — Automatisches Windows Setup & Konfiguration" -ForegroundColor Blue
Write-Host "====================================================================" -ForegroundColor Blue
Write-Host ""

# 1. Python-Installation überprüfen
Write-Host "🔎 Schritt 1: Python-Installation überprüfen..." -ForegroundColor Blue
$pythonCmd = $null

if (Get-Command "python3" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
}

if ($null -eq $pythonCmd) {
    Write-Host "❌ Fehler: Python wurde nicht gefunden!" -ForegroundColor Red
    Write-Host "Bitte installieren Sie Python 3.12+ (Python 3.13 empfohlen) von https://www.python.org/ und versuchen Sie es erneut."
    Write-Host "Stellen Sie sicher, dass bei der Installation 'Add Python to PATH' ausgewählt ist."
    Exit 1
}

$pyVersion = & $pythonCmd --version
Write-Host "✅ Python gefunden: $pyVersion (Kommando: $pythonCmd)" -ForegroundColor Green
Write-Host ""

# 2. Virtuelle Umgebung (.venv) anlegen
Write-Host "🐍 Schritt 2: Virtuelle Umgebung (.venv) erstellen..." -ForegroundColor Blue
$venvPath = Join-Path -Path $BackendDir -ChildPath ".venv"

if (Test-Path -Path $venvPath) {
    Write-Host "ℹ️ Eine virtuelle Umgebung existiert bereits unter backend/.venv." -ForegroundColor Yellow
    $recreate = Read-Host "Möchten Sie diese löschen und neu erstellen? (y/N)"
    if ($recreate -match "^[Yy]$") {
        Write-Host "Lösche alte Umgebung..."
        Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
        & $pythonCmd -m venv $venvPath
        Write-Host "✅ Neue virtuelle Umgebung erstellt." -ForegroundColor Green
    } else {
        Write-Host "Bestehende Umgebung wird beibehalten."
    }
} else {
    & $pythonCmd -m venv $venvPath
    Write-Host "✅ Virtuelle Umgebung erstellt unter backend/.venv." -ForegroundColor Green
}
Write-Host ""

# 3. Virtuelle Umgebung aktivieren & Abhängigkeiten installieren
Write-Host "📦 Schritt 3: Abhängigkeiten installieren..." -ForegroundColor Blue
$venvPython = Join-Path -Path $venvPath -ChildPath "Scripts\python.exe"
$venvPip = Join-Path -Path $venvPath -ChildPath "Scripts\pip.exe"

if (Test-Path -Path $venvPython) {
    Write-Host "Aktualisiere pip..."
    & $venvPython -m pip install --upgrade pip | Out-Null
    
    $reqPath = Join-Path -Path $BackendDir -ChildPath "requirements.txt"
    if (Test-Path -Path $reqPath) {
        Write-Host "Installiere Pakete aus requirements.txt (dies kann einen Moment dauern)..."
        & $venvPip install -r $reqPath
        Write-Host "✅ Abhängigkeiten erfolgreich installiert." -ForegroundColor Green
    } else {
        Write-Host "⚠️ requirements.txt nicht in backend/ gefunden!" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Fehler: Virtuelle Umgebung konnte nicht korrekt initialisiert werden (python.exe fehlt)." -ForegroundColor Red
    Exit 1
}
Write-Host ""

# 4. .env Datei anlegen und konfigurieren
Write-Host "🔑 Schritt 4: Umgebungsvariablen konfigurieren..." -ForegroundColor Blue
$envExamplePath = Join-Path -Path $BackendDir -ChildPath ".env.example"
$envPath = Join-Path -Path $BackendDir -ChildPath ".env"

$generateKey = $true
if (Test-Path -Path $envPath) {
    Write-Host "ℹ️ Eine .env Datei existiert bereits in backend/." -ForegroundColor Yellow
    $overwrite = Read-Host "Möchten Sie diese mit der .env.example überschreiben? (y/N)"
    if ($overwrite -match "^[Yy]$") {
        Copy-Item -Path $envExamplePath -Destination $envPath -Force
        $generateKey = $true
    } else {
        Write-Host "Bestehende .env Datei wird beibehalten."
        $generateKey = $false
    }
} else {
    Copy-Item -Path $envExamplePath -Destination $envPath
    Write-Host "✅ .env.example wurde nach .env kopiert." -ForegroundColor Green
    $generateKey = $true
}

if ($generateKey) {
    Write-Host "Generiere sicheren SECRET_KEY..."
    $randomSecret = & $venvPython -c "import secrets; print(secrets.token_hex(32))"
    
    # Text-Ersetzung und Speicherung als UTF-8 ohne BOM
    $content = [System.IO.File]::ReadAllText($envPath, [System.Text.Encoding]::UTF8)
    $content = $content.Replace('SECRET_KEY="supersecretkeychangeinproduction1234567890"', "SECRET_KEY=""$randomSecret""")
    [System.IO.File]::WriteAllText($envPath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "✅ Zufälliger SECRET_KEY wurde in backend/.env eingetragen." -ForegroundColor Green
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
    Write-Host "🤖 KI-Integration einrichten:" -ForegroundColor Blue
    Write-Host "Wenn Sie die KI-Features und den Stockkarten-Entwurf nutzen möchten,"
    Write-Host "können Sie hier Ihren Google Gemini API Key eingeben."
    Write-Host "Diesen erhalten Sie kostenlos unter: https://aistudio.google.com/"
    $geminiKey = Read-Host "Gemini API Key eingeben (oder [Enter] zum Überspringen)"
    
    if (-not [string]::IsNullOrEmpty($geminiKey)) {
        $content = [System.IO.File]::ReadAllText($envPath, [System.Text.Encoding]::UTF8)
        $content = $content.Replace('GEMINI_API_KEY=""', "GEMINI_API_KEY=""$geminiKey""")
        [System.IO.File]::WriteAllText($envPath, $content, [System.Text.Encoding]::UTF8)
        Write-Host "✅ GEMINI_API_KEY wurde in backend/.env gespeichert." -ForegroundColor Green
    } else {
        Write-Host "ℹ️ Übersprungen. Sie können den GEMINI_API_KEY später manuell in backend/.env eintragen." -ForegroundColor Yellow
    }
}
Write-Host ""

# 5. Abschluss und Anleitung
Write-Host "====================================================================" -ForegroundColor Green
Write-Host "🎉 Setup erfolgreich abgeschlossen!" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Gehen Sie wie folgt vor, um BeeBoard 2 zu starten:"
Write-Host ""
Write-Host "1. Backend-Datenbank initialisieren & starten:" -ForegroundColor Blue
Write-Host "   cd backend"
Write-Host "   # Virtuelle Umgebung aktivieren:"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   # Datenbank mit Standard-Daten befüllen:"
Write-Host "   python -m app.scripts.seed"
Write-Host "   # Server starten:"
Write-Host "   uvicorn app.main:app --reload --port 8000"
Write-Host ""
Write-Host "2. Frontend installieren & starten:" -ForegroundColor Blue
Write-Host "   cd frontend"
Write-Host "   npm install"
Write-Host "   npm run dev"
Write-Host ""
Write-Host "Viel Spaß mit BeeBoard 2! 🐝"
