# ==============================================================================
# DocxMath Studio - Tu Dong Cai Dat Moi Truong Tren Windows
# Ho tro: Windows 10, Windows 11, Windows Server (64-bit)
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "DocxMath Studio - Cai Dat Moi Truong Tu Dong"

function Print-Header {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "         DocxMath Studio - Trình Tự Động Cài Đặt Môi Trường Windows   " -ForegroundColor Cyan
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

Write-Host "Thư mục dự án: $projectRoot" -ForegroundColor Gray
Write-Host ""

# ------------------------------------------------------------------------------
# 1. KIỂM TRA VÀ CÀI ĐẶT PANDOC (Chuyển đổi công thức Word Equation OMML)
# ------------------------------------------------------------------------------
Write-Host "[1/4] Kiểm tra Pandoc (bắt buộc cho xuất công thức Word)..." -ForegroundColor Yellow

$hasPandoc = $false
try {
    $pandocVer = pandoc --version 2>$null
    if ($pandocVer) { $hasPandoc = $true }
} catch {
    $hasPandoc = $false
}

if (-not $hasPandoc) {
    # Kiểm tra trong các thư mục thông dụng
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
    Write-Host "  -> [OK] Pandoc đã sẵn sàng." -ForegroundColor Green
} else {
    Write-Host "  -> [!] Chưa tìm thấy Pandoc. Đang tiến hành tự động cài đặt..." -ForegroundColor Cyan
    
    $installed = $false
    # Cách 1: Dùng winget nếu có
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "  -> Đang cài đặt Pandoc qua Windows Package Manager (winget)..." -ForegroundColor Gray
        try {
            winget install -e --id JohnMacFarlane.Pandoc --silent --accept-package-agreements --accept-source-agreements
            Refresh-EnvPath
            if (Get-Command pandoc -ErrorAction SilentlyContinue) { $installed = $true }
        } catch {
            $installed = $false
        }
    }

    # Cách 2: Tải trực tiếp bản Portable từ GitHub Releases nếu winget không có hoặc lỗi
    if (-not $installed) {
        Write-Host "  -> Đang tải trực tiếp gói Pandoc chính thức từ GitHub..." -ForegroundColor Gray
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
            Write-Host "  -> [CANH BAO] Tải Pandoc tự động thất bại: $_" -ForegroundColor Red
        } finally {
            if (Test-Path $tempZip) { Remove-Item $tempZip -Force -ErrorAction SilentlyContinue }
            if (Test-Path $tempExtract) { Remove-Item $tempExtract -Recurse -Force -ErrorAction SilentlyContinue }
        }
    }

    if ($installed -or (Get-Command pandoc -ErrorAction SilentlyContinue)) {
        Write-Host "  -> [OK] Đã cài đặt Pandoc thành công!" -ForegroundColor Green
    } else {
        Write-Host "  -> [CHÚ Ý] Không thể tự động cài Pandoc. Bạn có thể cài thủ công từ: https://pandoc.org/installing.html" -ForegroundColor Red
    }
}
Write-Host ""

# ------------------------------------------------------------------------------
# 2. KIỂM TRA VÀ CÀI ĐẶT PYTHON (FastAPI & Xử lý tài liệu Word)
# ------------------------------------------------------------------------------
Write-Host "[2/4] Kiểm tra Python (phiên bản 3.10 trở lên)..." -ForegroundColor Yellow

$hasPython = $false
$pythonCmd = "python"

try {
    $pyVer = python --version 2>$null
    if ($pyVer -like "*Python 3.*") {
        $hasPython = $true
    }
} catch {
    $hasPython = $false
}

if (-not $hasPython) {
    try {
        $pyVer = py -3 --version 2>$null
        if ($pyVer -like "*Python 3.*") {
            $hasPython = $true
            $pythonCmd = "py -3"
        }
    } catch {
        $hasPython = $false
    }
}

if (-not $hasPython) {
    # Quét các thư mục cài đặt Python thông dụng
    $commonPyPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe"
    )
    foreach ($p in $commonPyPaths) {
        if (Test-Path $p) {
            $hasPython = $true
            $pyDir = Split-Path -Parent $p
            $env:Path = "$pyDir;$pyDir\Scripts;$env:Path"
            $pythonCmd = $p
            break
        }
    }
}

if ($hasPython) {
    Write-Host "  -> [OK] Python đã sẵn sàng: $(& $pythonCmd --version)" -ForegroundColor Green
} else {
    Write-Host "  -> [!] Chưa tìm thấy Python. Đang tiến hành cài đặt Python 3.11 tự động..." -ForegroundColor Cyan
    
    $pyInstalled = $false
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "  -> Đang cài đặt Python qua winget..." -ForegroundColor Gray
        try {
            winget install -e --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
            Refresh-EnvPath
            $pyInstalled = $true
        } catch {
            $pyInstalled = $false
        }
    }

    if (-not $pyInstalled) {
        Write-Host "  -> Đang tải bản cài đặt Python chính thức từ python.org..." -ForegroundColor Gray
        $pyUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        $pyInstaller = "$env:TEMP\python_installer.exe"
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller -UseBasicParsing
            Write-Host "  -> Đang cài đặt Python (chế độ nền)..." -ForegroundColor Gray
            Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 SimpleInstall=1" -Wait
            Refresh-EnvPath
            $pyInstalled = $true
        } catch {
            Write-Host "  -> [LOI] Tải và cài đặt Python thất bại: $_" -ForegroundColor Red
        } finally {
            if (Test-Path $pyInstaller) { Remove-Item $pyInstaller -Force -ErrorAction SilentlyContinue }
        }
    }

    Refresh-EnvPath
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
        Write-Host "  -> [OK] Đã cài đặt Python thành công!" -ForegroundColor Green
    } else {
        Write-Host "  -> [LƯU Ý] Nếu vừa cài xong Python, vui lòng đóng cửa sổ này và mở lại để Windows nhận diện PATH." -ForegroundColor Yellow
    }
}
Write-Host ""

# ------------------------------------------------------------------------------
# 3. CÀI ĐẶT THƯ VIỆN PYTHON (backend/requirements.txt)
# ------------------------------------------------------------------------------
Write-Host "[3/4] Cài đặt các thư viện Python cần thiết..." -ForegroundColor Yellow
try {
    Write-Host "  -> Đang cập nhật pip và cài đặt FastAPI, python-docx, uvicorn, beautifulsoup4..." -ForegroundColor Gray
    & $pythonCmd -m pip install --upgrade pip --quiet
    & $pythonCmd -m pip install -r "$projectRoot\backend\requirements.txt" --quiet
    Write-Host "  -> [OK] Đã cài đặt đầy đủ các thư viện Python!" -ForegroundColor Green
} catch {
    Write-Host "  -> [CANH BAO] Có lỗi nhỏ khi chạy pip, kiểm tra lại: $_" -ForegroundColor Yellow
}
Write-Host ""

# ------------------------------------------------------------------------------
# 4. KIỂM TRA BẢN BUILD GIAO DIỆN FRONTEND (Web UI)
# ------------------------------------------------------------------------------
Write-Host "[4/4] Kiểm tra giao diện người dùng (Frontend)..." -ForegroundColor Yellow

$distIndex = "$projectRoot\frontend\dist\index.html"
if (Test-Path $distIndex) {
    Write-Host "  -> [OK] Giao diện người dùng đã được biên dịch sẵn sàng." -ForegroundColor Green
} else {
    Write-Host "  -> [!] Chưa có bản build giao diện. Đang kiểm tra Node.js để biên dịch..." -ForegroundColor Cyan
    $hasNode = $false
    try {
        if (Get-Command npm -ErrorAction SilentlyContinue) { $hasNode = $true }
    } catch {
        $hasNode = $false
    }

    if (-not $hasNode) {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host "  -> Đang cài đặt Node.js LTS qua winget..." -ForegroundColor Gray
            winget install -e --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
            Refresh-EnvPath
        }
    }

    if (Get-Command npm -ErrorAction SilentlyContinue) {
        Write-Host "  -> Đang cài đặt thư viện frontend và biên dịch..." -ForegroundColor Gray
        Push-Location "$projectRoot\frontend"
        npm install --quiet
        npm run build
        Pop-Location
        Write-Host "  -> [OK] Biên dịch giao diện hoàn tất!" -ForegroundColor Green
    } else {
        Write-Host "  -> [CANH BAO] Chưa tìm thấy Node.js. Bạn có thể cài đặt Node.js từ https://nodejs.org" -ForegroundColor Yellow
    }
}
Write-Host ""

# ------------------------------------------------------------------------------
# TỔNG KẾT & KHỞI ĐỘNG
# ------------------------------------------------------------------------------
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "         CHÚC MỪNG! HỆ THỐNG ĐÃ ĐƯỢC THIẾT LẬP HOÀN TẤT               " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Từ bây giờ, trên bất kỳ máy Windows nào, bạn chỉ cần nhấp đúp vào:" -ForegroundColor White
Write-Host "  -> run_windows.bat" -ForegroundColor Cyan
Write-Host "để khởi động DocxMath Studio và tự động mở trên trình duyệt." -ForegroundColor White
Write-Host ""

$answer = Read-Host "Bạn có muốn khởi động DocxMath Studio ngay bây giờ không? (Y/N)"
if ($answer -eq 'Y' -or $answer -eq 'y' -or $answer -eq '') {
    Write-Host "Đang khởi động ứng dụng..." -ForegroundColor Cyan
    Start-Process -FilePath "$projectRoot\run_windows.bat"
}
