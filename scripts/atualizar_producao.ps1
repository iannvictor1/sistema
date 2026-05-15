param(
    [string]$ProjectDir = (Split-Path -Parent $PSScriptRoot),
    [string]$BackendService = "",
    [string]$FrontendService = ""
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Restart-OptionalService($Name) {
    if ([string]::IsNullOrWhiteSpace($Name)) {
        return
    }

    Write-Step "Reiniciando servico: $Name"
    Restart-Service -Name $Name -Force
}

function Assert-SupportedPython($PythonExe) {
    $versionText = & $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $parts = $versionText.Split(".")
    $major = [int]$parts[0]
    $minor = [int]$parts[1]

    if ($major -ne 3 -or $minor -lt 11 -or $minor -gt 12) {
        throw "Python $versionText nao e suportado por estas dependencias. Use Python 3.11 ou 3.12, preferencialmente 3.12."
    }
}

Write-Step "Entrando no projeto"
Set-Location -LiteralPath $ProjectDir

Write-Step "Atualizando codigo pelo Git"
git pull

Write-Step "Atualizando dependencias Python"
if (!(Test-Path -LiteralPath ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

Assert-SupportedPython ".\.venv\Scripts\python.exe"
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Step "Atualizando frontend React"
Set-Location -LiteralPath (Join-Path $ProjectDir "frontend-react")
npm install
npm run build

Set-Location -LiteralPath $ProjectDir

Restart-OptionalService -Name $BackendService
Restart-OptionalService -Name $FrontendService

Write-Host ""
Write-Host "Atualizacao concluida." -ForegroundColor Green
