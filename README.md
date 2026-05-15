# Sistema de Bonificacao

Sistema com backend FastAPI, banco PostgreSQL/SQLite conforme ambiente, frontend Streamlit legado e frontend React em `frontend-react`.

Em producao, o fluxo recomendado agora e:

- PostgreSQL instalado localmente na maquina de producao, como servico do Windows;
- backend FastAPI rodando na porta `8000`;
- frontend React compilado em `frontend-react/dist` e servido pelo proprio FastAPI;
- atualizacoes feitas por Git, sem substituicao manual das pastas `app` e `frontend`.

## Atualizacao em Producao

Fluxo recomendado:

1. Fazer as alteracoes no computador de desenvolvimento.
2. Enviar para o repositorio:

```powershell
git add .
git commit -m "Descricao da alteracao"
git push
```

3. No computador de producao, atualizar pelo script:

```powershell
.\scripts\atualizar_producao.ps1
```

Se o sistema estiver rodando como servico do Windows, informe o nome do servico do backend:

```powershell
.\scripts\atualizar_producao.ps1 -BackendService "BonificacaoBackend"
```

Para disparar a atualizacao remotamente a partir do computador de desenvolvimento, habilite PowerShell Remoting/WinRM na maquina de producao e execute:

```powershell
.\scripts\atualizar_remoto.ps1 -ComputerName "NOME-OU-IP-DA-PRODUCAO" -ProjectDir "C:\bonificacao_system" -BackendService "BonificacaoBackend"
```

## Primeira Instalacao no Computador de Producao

1. Instalar Git, Python, Node.js e PostgreSQL local.
2. Clonar o repositorio:

```powershell
git clone URL_DO_REPOSITORIO bonificacao_system
cd bonificacao_system
```

3. Criar o banco PostgreSQL local:

```powershell
.\scripts\preparar_postgres_local.ps1
```

Esse script cria o usuario `bonificacao`, o banco `bonificacao_db` e grava um `.env` local apontando para:

```text
postgresql+psycopg://bonificacao:bonificacao123@127.0.0.1:5432/bonificacao_db
```

4. Criar ambiente Python e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

5. Instalar e compilar o frontend React:

```powershell
cd frontend-react
npm install
npm run build
cd ..
```

6. Rodar o backend:

```powershell
.\scripts\iniciar_backend_producao.ps1
```

Depois acesse:

```text
http://127.0.0.1:8000
```

Tambem existe um arquivo `.env.example` como modelo. Em producao, crie ou mantenha um `.env` real com os dados do computador final. O `.env` nao deve ser enviado para o Git.

## Servico do Windows

Para producao, prefira criar um servico chamado `BonificacaoBackend` apontando para:

```powershell
powershell.exe -ExecutionPolicy Bypass -File "C:\bonificacao_system\scripts\iniciar_backend_producao.ps1"
```

Ferramentas como NSSM facilitam esse cadastro porque mantem o processo Python como servico e permitem reiniciar automaticamente em caso de falha.

## Migrar SQLite para PostgreSQL

Use este fluxo quando a producao antiga ainda usa o banco SQLite `bonificacao.db`.

Primeiro prepare o PostgreSQL local:

```powershell
.\scripts\preparar_postgres_local.ps1
```

Depois migre o SQLite para o PostgreSQL:

```powershell
$env:PGCLIENTENCODING="UTF8"
$env:DATABASE_URL="postgresql+psycopg://bonificacao:bonificacao123@127.0.0.1:5432/bonificacao_db"
.\.venv\Scripts\python.exe scripts\migrar_sqlite_para_postgres.py
```

Por padrao, o script:

- cria um backup do SQLite em `backups/`;
- cria as tabelas no PostgreSQL se ainda nao existirem;
- copia funcionarios, lancamentos e frequencias;
- preserva os IDs originais;
- ajusta as sequencias do PostgreSQL ao final.

Se quiser apagar os dados atuais do PostgreSQL antes de importar, use `--replace`:

```powershell
.\.venv\Scripts\python.exe scripts\migrar_sqlite_para_postgres.py --replace
```

Use `--replace` somente em banco de teste ou depois de backup.

Na primeira migracao da producao, normalmente use `--replace` se o PostgreSQL local estiver vazio ou tiver apenas dados de teste:

```powershell
.\.venv\Scripts\python.exe scripts\migrar_sqlite_para_postgres.py --replace
```

## Migrar PostgreSQL da Docker para PostgreSQL Local

Use esta secao apenas se os dados atuais estiverem em um PostgreSQL exposto pela Docker na porta `55432`. Se a producao antiga usa SQLite, use a secao anterior.

Se os dados atuais estao no PostgreSQL exposto pela Docker na porta `55432` e o PostgreSQL local esta na porta `5432`, primeiro prepare o banco local:

```powershell
.\scripts\preparar_postgres_local.ps1
```

Depois copie os dados:

```powershell
.\scripts\migrar_postgres_docker_para_local.ps1
```

Se o banco local ja tiver dados de teste e voce quiser substituir pelo conteudo da Docker:

```powershell
.\scripts\migrar_postgres_docker_para_local.ps1 -Replace
```

O script gera um backup em `backups/` antes de restaurar no PostgreSQL local.

## Observacoes

- Nao versionar `.venv`, `node_modules`, builds, banco local ou backups.
- Antes de atualizacoes importantes em producao, faca backup do banco.
- O script `scripts/atualizar_producao.ps1` nao apaga dados do banco.
