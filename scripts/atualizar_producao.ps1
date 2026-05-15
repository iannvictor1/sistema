param(
    [string]$ProjectDir = (Split-Path -Parent $PSScriptRoot),
    [string]$BackendService = "",
    [string]$FrontendService = "",
    [string]$BackendTask = "",
    [string]$FrontendTask = ""
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

function Restart-OptionalScheduledTask($Name) {
    if ([string]::IsNullOrWhiteSpace($Name)) {
        return
    }

    Write-Step "Reiniciando tarefa agendada: $Name"
    $task = Get-ScheduledTask | Where-Object { $_.TaskName -eq $Name } | Select-Object -First 1

    if (!$task) {
        $knownTasks = Get-ScheduledTask |
            Where-Object { $_.TaskName -like "*Bonificacao*" -or $_.TaskName -like "*Bonificação*" } |
            Select-Object -ExpandProperty TaskName

        $hint = if ($knownTasks) {
            " Tarefas parecidas encontradas: $($knownTasks -join ', ')."
        } else {
            " Nenhuma tarefa parecida foi encontrada. Crie a tarefa com scripts\criar_tarefa_backend_producao.ps1."
        }

        throw "Tarefa agendada '$Name' nao encontrada.$hint"
    }

    if ($task.State -eq "Running") {
        schtasks.exe /End /TN $task.TaskName | Out-Null
        Start-Sleep -Seconds 2
    }

    schtasks.exe /Run /TN $task.TaskName | Out-Null
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
Restart-OptionalScheduledTask -Name $BackendTask
Restart-OptionalScheduledTask -Name $FrontendTask

Write-Host ""
Write-Host "Atualizacao concluida." -ForegroundColor Green
