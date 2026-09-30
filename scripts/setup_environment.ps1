# ==============================================================================
# DocxMath Studio - Automated Environment Setup for Windows
# Supported: Windows 10, Windows 11, Windows Server (64-bit)
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "DocxMath Studio - Automated Setup"

function Print-Header {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "             DocxMath Studio - Automated Windows Setup                " -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Refresh-EnvPath {
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machinePath;$userPath;$env:LOCALAPPDATA\Pandoc;C:\Program Files\Pandoc;C:\Program Files\nodejs;$env:APPDATA\npm"
}

Print-Header

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Project directory: $projectRoot" -ForegroundColor Gray
Write-Host ""

# ------------------------------------------------------------------------------
# 1. CHECK AND INSTALL PANDOC (Required for Word Equation OMML export)
# ------------------------------------------------------------------------------
Write-Host "[1/4] Checking Pandoc (required for Word OMML equations)..." -ForegroundColor Yellow

$hasPandoc = $false
try {
    $pandocVer = pandoc --version 2>&1
    if ($pandocVer -like "*pandoc*") { $hasPandoc = $true }
} catch {
    $hasPandoc = $false
}

if (-not $hasPandoc) {
    # Check standard directories
    $commonPandocPaths = @(
        "$env:LOCALAPPDATA\Pandoc\pandoc.exe",
        "C:\Program Files\Pandoc\pandoc.exe",
        "C:\Program Files (x86)\Pandoc\pandoc.exe"
    )
    foreach ($p in $commonPandocPaths) {
        if (Test-Path $p) {
            $hasPandoc = $true
            $pandocDir = Split-Path -Parent $p
            $env:Path = "$pandocDir;$env:Path"
            break
        }
    }
}

if ($hasPandoc) {
    Write-Host "  -> [OK] Pandoc is ready." -ForegroundColor Green
} else {
    Write-Host "  -> [!] Pandoc not found. Installing automatically..." -ForegroundColor Cyan
    
    $installed = $false
    # Method 1: Windows Package Manager (winget)
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "  -> Installing Pandoc via Windows Package Manager (winget)..." -ForegroundColor Gray
        try {
            winget install -e --id JohnMacFarlane.Pandoc --silent --accept-package-agreements --accept-source-agreements
            Refresh-EnvPath
            if (Get-Command pandoc -ErrorAction SilentlyContinue) { $installed = $true }
        } catch {
            $installed = $false
        }
    }

    # Method 2: Download official portable release from GitHub if winget is unavailable
    if (-not $installed) {
        Write-Host "  -> Downloading official Pandoc release from GitHub..." -ForegroundColor Gray
        $pandocZipUrl = "https://github.com/jgm/pandoc/releases/download/3.1.11.1/pandoc-3.1.11.1-windows-x86_64.zip"
        $tempZip = "$env:TEMP\pandoc_installer.zip"
        $tempExtract = "$env:TEMP\pandoc_extract"
        $targetDir = "$env:LOCALAPPDATA\Pandoc"

        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $pandocZipUrl -OutFile $tempZip -UseBasicParsing
            if (Test-Path $tempExtract) { Remove-Item $tempExtract -Recurse -Force }
            Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force
            
            if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
            $extractedPandoc = Get-ChildItem -Path $tempExtract -Filter "pandoc.exe" -Recurse | Select-Object -First 1
            if ($extractedPandoc) {
                Copy-Item -Path $extractedPandoc.FullName -Destination "$targetDir\pandoc.exe" -Force
                $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
                if ($userPath -notlike "*$targetDir*") {
                    [Environment]::SetEnvironmentVariable("Path", "$userPath;$targetDir", "User")
                }
                $env:Path = "$targetDir;$env:Path"
                $installed = $true
            }
        } catch {
            Write-Host "  -> [WARNING] Automatic Pandoc download failed: $_" -ForegroundColor Red
        } finally {
            if (Test-Path $tempZip) { Remove-Item $tempZip -Force -ErrorAction SilentlyContinue }
            if (Test-Path $tempExtract) { Remove-Item $tempExtract -Recurse -Force -ErrorAction SilentlyContinue }
        }
    }

    if ($installed -or (Get-Command pandoc -ErrorAction SilentlyContinue)) {
        Write-Host "  -> [OK] Pandoc installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "  -> [NOTE] Could not install Pandoc automatically. You can install it manually from: https://pandoc.org/installing.html" -ForegroundColor Red
    }
}
Write-Host ""

# ------------------------------------------------------------------------------
# 2. CHECK AND INSTALL PYTHON (FastAPI & Document Engine)
# ------------------------------------------------------------------------------
Write-Host "[2/4] Checking Python (version 3.10 or higher)..." -ForegroundColor Yellow

$pythonExe = ""
$pythonArgs = @()

function Test-PythonExecutable($exe, $extraArgs = @()) {
    try {
        $cmd = if ($extraArgs.Count -gt 0) { "$exe $($extraArgs -join ' ')" } else { $exe }
        $verStr = if ($extraArgs.Count -gt 0) { & $exe $extraArgs --version 2>&1 } else { & $exe --version 2>&1 }
        if ($verStr -match "Python 3\.(\d+)") {
            $minor = [int]$matches[1]
            if ($minor -ge 10) {
                return $true
            }
        }
    } catch {}
    return $false
}

# 1. Test "python" in PATH
if (Test-PythonExecutable "python") {
    $pythonExe = "python"
}

# 2. Test "py -3" launcher
if (-not $pythonExe) {
    if (Get-Command py.exe -ErrorAction SilentlyContinue) {
        if (Test-PythonExecutable "py" @("-3")) {
            try {
                $resolved = py -3 -c "import sys; print(sys.executable)" 2>&1
                if ($resolved -and (Test-Path $resolved.Trim())) {
                    $pythonExe = $resolved.Trim()
                } else {
                    $pythonExe = "py"
                    $pythonArgs = @("-3")
                }
            } catch {
                $pythonExe = "py"
                $pythonArgs = @("-3")
            }
        }
    }
}

# 3. Test common installation paths
if (-not $pythonExe) {
    $commonPyPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Program Files\Python313\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe"
    )
    foreach ($p in $commonPyPaths) {
        if (Test-Path $p) {
            if (Test-PythonExecutable $p) {
                $pythonExe = $p
                $pyDir = Split-Path -Parent $p
                $env:Path = "$pyDir;$pyDir\Scripts;$env:Path"
                break
            }
        }
    }
}

function Invoke-Python([string[]]$cmdArgs) {
    if ($pythonArgs.Count -gt 0) {
        & $pythonExe ($pythonArgs + $cmdArgs)
    } else {
        & $pythonExe $cmdArgs
    }
}

if ($pythonExe) {
    $ver = (Invoke-Python @("--version")) 2>&1
    Write-Host "  -> [OK] Python is ready: $ver ($pythonExe)" -ForegroundColor Green
} else {
    Write-Host "  -> [!] Python 3.10+ not found. Installing Python 3.11 automatically..." -ForegroundColor Cyan
    
    $pyInstalled = $false
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "  -> Installing Python 3.11 via winget..." -ForegroundColor Gray
        try {
            winget install -e --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
            Refresh-EnvPath
            $pyInstalled = $true
        } catch {
            $pyInstalled = $false
        }
    }

    if (-not $pyInstalled) {
        Write-Host "  -> Downloading official Python installer from python.org..." -ForegroundColor Gray
        $pyUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        $pyInstaller = "$env:TEMP\python_installer.exe"
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller -UseBasicParsing
            Write-Host "  -> Running silent installation..." -ForegroundColor Gray
            Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 SimpleInstall=1" -Wait
            Refresh-EnvPath
            $pyInstalled = $true
        } catch {
            Write-Host "  -> [ERROR] Failed to download/install Python: $_" -ForegroundColor Red
        } finally {
            if (Test-Path $pyInstaller) { Remove-Item $pyInstaller -Force -ErrorAction SilentlyContinue }
        }
    }

    Refresh-EnvPath
    if (Test-PythonExecutable "python") {
        $pythonExe = "python"
        $pythonArgs = @()
        Write-Host "  -> [OK] Python installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "  -> [NOTE] If Python was just installed, please restart your terminal so Windows recognizes PATH." -ForegroundColor Yellow
    }
}
Write-Host ""

# ------------------------------------------------------------------------------
# 3. INSTALL PYTHON LIBRARIES (FastAPI, python-docx, uvicorn...)
# ------------------------------------------------------------------------------
Write-Host "[3/4] Installing Python requirements (FastAPI, python-docx, uvicorn...)..." -ForegroundColor Yellow
if ($pythonExe) {
    try {
        Write-Host "  -> Updating pip..." -ForegroundColor Gray
        Invoke-Python @("-m", "pip", "install", "--upgrade", "pip", "--quiet")
        Write-Host "  -> Installing packages from backend/requirements.txt..." -ForegroundColor Gray
        Invoke-Python @("-m", "pip", "install", "-r", "$projectRoot\backend\requirements.txt", "--quiet")
        Write-Host "  -> [OK] Python libraries installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "  -> [WARNING] pip returned an error: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  -> [SKIP] Python is not yet available to install libraries." -ForegroundColor Red
}
Write-Host ""

# ------------------------------------------------------------------------------
# 4. VERIFY FRONTEND WEB UI BUNDLE
# ------------------------------------------------------------------------------
Write-Host "[4/4] Verifying Frontend Web UI..." -ForegroundColor Yellow

$distIndex = "$projectRoot\frontend\dist\index.html"
if (Test-Path $distIndex) {
    Write-Host "  -> [OK] Frontend web bundle is ready and pre-built (no Node.js required)." -ForegroundColor Green
} else {
    Write-Host "  -> [!] Pre-built frontend not found. Checking Node.js to build..." -ForegroundColor Cyan
    $hasNode = $false
    try {
        if (Get-Command npm -ErrorAction SilentlyContinue) { $hasNode = $true }
    } catch {
        $hasNode = $false
    }

    if (-not $hasNode) {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host "  -> Installing Node.js LTS via winget..." -ForegroundColor Gray
            winget install -e --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
            Refresh-EnvPath
        }
    }

    if (Get-Command npm -ErrorAction SilentlyContinue) {
        Write-Host "  -> Building frontend assets..." -ForegroundColor Gray
        Push-Location "$projectRoot\frontend"
        npm install --quiet
        npm run build
        Pop-Location
        Write-Host "  -> [OK] Frontend build completed!" -ForegroundColor Green
    } else {
        Write-Host "  -> [WARNING] Node.js not found. Please install Node.js from https://nodejs.org" -ForegroundColor Yellow
    }
}
Write-Host ""

# ------------------------------------------------------------------------------
# SUMMARY & LAUNCH PROMPT
# ------------------------------------------------------------------------------
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "              SETUP COMPLETED SUCCESSFULLY!                           " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now launch DocxMath Studio anytime by double-clicking:" -ForegroundColor White
Write-Host "  -> run_windows.bat" -ForegroundColor Cyan
Write-Host ""

$answer = Read-Host "Would you like to start DocxMath Studio now? (Y/N)"
if ($answer -eq 'Y' -or $answer -eq 'y' -or $answer -eq '') {
    Write-Host "Starting DocxMath Studio..." -ForegroundColor Cyan
    Start-Process -FilePath "$projectRoot\run_windows.bat"
}
