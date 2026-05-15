param(
    [string]$ProjectDir = (Split-Path -Parent $PSScriptRoot),
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $ProjectDir

function Assert-SupportedPython($PythonExe) {
    $versionText = & $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $parts = $versionText.Split(".")
    $major = [int]$parts[0]
    $minor = [int]$parts[1]

    if ($major -ne 3 -or $minor -lt 11 -or $minor -gt 12) {
        throw "Python $versionText nao e suportado por estas dependencias. Use Python 3.11 ou 3.12, preferencialmente 3.12."
    }
}

$envFile = Join-Path $ProjectDir ".env"
if (Test-Path -LiteralPath $envFile) {
    Get-Content -LiteralPath $envFile | ForEach-Object {
        $line = $_.Trim()
        if (!$line -or $line.StartsWith("#") -or !$line.Contains("=")) {
            return
        }

        $parts = $line.Split("=", 2)
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
    }
}

if (!$env:PGCLIENTENCODING) {
    $env:PGCLIENTENCODING = "UTF8"
}

if (!(Test-Path -LiteralPath ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

Assert-SupportedPython ".\.venv\Scripts\python.exe"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host $HostAddress --port $Port
