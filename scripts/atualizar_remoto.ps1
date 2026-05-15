param(
    [Parameter(Mandatory = $true)]
    [string]$ComputerName,

    [string]$ProjectDir = "C:\bonificacao_system",
    [string]$BackendService = "",
    [string]$FrontendService = "",
    [string]$BackendTask = "",
    [string]$FrontendTask = "",
    [string]$UserName = ""
)

$ErrorActionPreference = "Stop"

$credential = $null
if (![string]::IsNullOrWhiteSpace($UserName)) {
    $credential = Get-Credential -UserName $UserName -Message "Credenciais da maquina de producao"
}

$script = {
    param($RemoteProjectDir, $RemoteBackendService, $RemoteFrontendService, $RemoteBackendTask, $RemoteFrontendTask)

    Set-Location -LiteralPath $RemoteProjectDir
    & .\scripts\atualizar_producao.ps1 `
        -ProjectDir $RemoteProjectDir `
        -BackendService $RemoteBackendService `
        -FrontendService $RemoteFrontendService `
        -BackendTask $RemoteBackendTask `
        -FrontendTask $RemoteFrontendTask
}

$params = @{
    ComputerName = $ComputerName
    ScriptBlock = $script
    ArgumentList = @($ProjectDir, $BackendService, $FrontendService, $BackendTask, $FrontendTask)
}

if ($credential) {
    $params.Credential = $credential
}

Invoke-Command @params
