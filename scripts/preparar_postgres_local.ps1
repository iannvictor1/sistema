param(
    [string]$DbName = "bonificacao_db",
    [string]$DbUser = "bonificacao",
    [string]$DbPassword = "bonificacao123",
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 5432,
    [string]$PostgresAdminUser = "postgres",
    [string]$PostgresAdminPassword = "",
    [string]$ProjectDir = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-PostgresScalar($Sql) {
    $result = & psql -h $HostAddress -p $Port -U $PostgresAdminUser -d postgres -tAc $Sql
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel conectar ao PostgreSQL local com o usuario '$PostgresAdminUser'. Confira a senha do usuario postgres e se o servico esta rodando na porta $Port."
    }

    if ($null -eq $result) {
        return ""
    }

    return ($result | Select-Object -First 1).ToString().Trim()
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

Write-Step "Verificando psql"
Add-PostgresBinToPath
if (!(Get-Command psql -ErrorAction SilentlyContinue)) {
    throw "psql nao foi encontrado no PATH. Instale o PostgreSQL local e marque a opcao de adicionar as ferramentas ao PATH, ou abra este script no terminal do PostgreSQL."
}

if (![string]::IsNullOrWhiteSpace($PostgresAdminPassword)) {
    $env:PGPASSWORD = $PostgresAdminPassword
}

Write-Step "Criando usuario, se necessario"
$roleExists = Invoke-PostgresScalar "SELECT 1 FROM pg_roles WHERE rolname = '$DbUser';"
if ($roleExists -ne "1") {
    & psql -h $HostAddress -p $Port -U $PostgresAdminUser -d postgres -c "CREATE USER $DbUser WITH PASSWORD '$DbPassword';"
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel criar o usuario '$DbUser'."
    }
}

Write-Step "Criando banco, se necessario"
$dbExists = Invoke-PostgresScalar "SELECT 1 FROM pg_database WHERE datname = '$DbName';"
if ($dbExists -ne "1") {
    & createdb -h $HostAddress -p $Port -U $PostgresAdminUser -O $DbUser $DbName
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel criar o banco '$DbName'."
    }
}

Write-Step "Aplicando permissoes"
& psql -h $HostAddress -p $Port -U $PostgresAdminUser -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DbName TO $DbUser;"
if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel aplicar permissoes no banco '$DbName'."
}

if (![string]::IsNullOrWhiteSpace($PostgresAdminPassword)) {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

Write-Step "Atualizando .env do projeto"
$envPath = Join-Path $ProjectDir ".env"
@(
    "PGCLIENTENCODING=UTF8"
    "DATABASE_URL=postgresql+psycopg://${DbUser}:${DbPassword}@${HostAddress}:${Port}/${DbName}"
) | Set-Content -LiteralPath $envPath -Encoding UTF8

Write-Host ""
Write-Host "PostgreSQL local configurado. DATABASE_URL gravada em .env." -ForegroundColor Green
