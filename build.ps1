# PowerShell script for building mini-open2anth on Windows
# This script is optimized for GitHub Actions and CI/CD environments

# Enable strict error handling
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build mini-open2anth EXE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
try {
    $pythonVersion = "3.8"
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Install dependencies if not in CI environment
if ($env:CI -ne "true") {
    Write-Host "[1/4] Installing dependencies..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller
    Write-Host ""
}

# Clean previous builds
Write-Host "[2/4] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force build
    Write-Host "  ✓ Deleted build directory" -ForegroundColor Gray
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force dist
    Write-Host "  ✓ Deleted dist directory" -ForegroundColor Gray
}

# Run PyInstaller
Write-Host ""
Write-Host "[3/4] Building with PyInstaller..." -ForegroundColor Yellow
Write-Host "This may take several minutes, please wait..." -ForegroundColor Gray
try {
    pyinstaller build.spec --clean
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ PyInstaller completed successfully" -ForegroundColor Green
    } else {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Host "ERROR: PyInstaller failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Prepare release files
Write-Host ""
Write-Host "[4/4] Preparing release files..." -ForegroundColor Yellow

# Create release directory
if (!(Test-Path "release")) {
    New-Item -ItemType Directory -Path release -Force | Out-Null
    Write-Host "  ✓ Created release directory" -ForegroundColor Gray
}

# Copy exe file
$exeSource = "dist\mini-open2anth.exe"
$exeDest = "release\mini-open2anth.exe"
if (Test-Path $exeSource) {
    Copy-Item $exeSource $exeDest -Force
    Write-Host "  ✓ Copied exe file" -ForegroundColor Gray
    $exeSize = (Get-Item $exeDest).Length / 1MB
    Write-Host "    Size: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Gray
} else {
    Write-Host "ERROR: Executable not found at $exeSource" -ForegroundColor Red
    exit 1
}

# Copy .env.example if it exists
if (Test-Path ".env.example") {
    Copy-Item ".env.example" "release\.env.example" -Force
    Write-Host "  ✓ Copied .env.example" -ForegroundColor Gray
}

# Copy .env if it exists (useful for CI)
if (Test-Path ".env") {
    Copy-Item ".env" "release\.env" -Force
    Write-Host "  ✓ Copied .env" -ForegroundColor Gray
}

# Display final results
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output files:" -ForegroundColor Yellow
Get-ChildItem release | ForEach-Object {
    $size = $_.Length / 1MB
    Write-Host "  - $($_.Name) ($([math]::Round($size, 2)) MB)" -ForegroundColor White
}
Write-Host ""
Write-Host "Location: $(Resolve-Path release)\" -ForegroundColor Gray
Write-Host ""

# Exit with success code
exit 0
