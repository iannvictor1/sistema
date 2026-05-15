param(
    [string]$SourceHost = "127.0.0.1",
    [int]$SourcePort = 55432,
    [string]$SourceDb = "bonificacao_db",
    [string]$SourceUser = "bonificacao",
    [string]$SourcePassword = "bonificacao123",

    [string]$TargetHost = "127.0.0.1",
    [int]$TargetPort = 5432,
    [string]$TargetDb = "bonificacao_db",
    [string]$TargetUser = "bonificacao",
    [string]$TargetPassword = "bonificacao123",

    [string]$ProjectDir = (Split-Path -Parent $PSScriptRoot),
    [switch]$Replace
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Add-PostgresBinToPath() {
    if (Get-Command psql -ErrorAction SilentlyContinue) {
        return
    }

    $postgresBin = Get-ChildItem "C:\Program Files\PostgreSQL" -Recurse -Filter psql.exe -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -like "*\bin\psql.exe" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1

    if ($postgresBin) {
        $binDir = Split-Path -Parent $postgresBin.FullName
        $env:Path = "$binDir;$env:Path"
    }
}

Add-PostgresBinToPath

if (!(Get-Command pg_dump -ErrorAction SilentlyContinue)) {
    throw "pg_dump nao foi encontrado no PATH. Instale as ferramentas do PostgreSQL local ou abra este script no terminal do PostgreSQL."
}

if (!(Get-Command pg_restore -ErrorAction SilentlyContinue)) {
    throw "pg_restore nao foi encontrado no PATH. Instale as ferramentas do PostgreSQL local ou abra este script no terminal do PostgreSQL."
}

$backupDir = Join-Path $ProjectDir "backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $backupDir "postgres_docker_${SourceDb}_${timestamp}.dump"

Write-Step "Gerando backup do PostgreSQL da Docker em $backupFile"
$env:PGPASSWORD = $SourcePassword
& pg_dump `
    -h $SourceHost `
    -p $SourcePort `
    -U $SourceUser `
    -d $SourceDb `
    -Fc `
    -f $backupFile

Write-Step "Restaurando backup no PostgreSQL local"
$env:PGPASSWORD = $TargetPassword

$restoreArgs = @(
    "-h", $TargetHost,
    "-p", $TargetPort,
    "-U", $TargetUser,
    "-d", $TargetDb,
    "--no-owner"
)

if ($Replace) {
    $restoreArgs += @("--clean", "--if-exists")
}

$restoreArgs += $backupFile
& pg_restore @restoreArgs

Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Migracao concluida. Backup preservado em: $backupFile" -ForegroundColor Green
