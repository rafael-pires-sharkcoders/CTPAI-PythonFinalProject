@echo off
chcp 65001 > nul

echo Iniciando servicos InfluxDB e Grafana...

REM Verificar se Docker esta instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Docker nao esta instalado. Por favor, instale o Docker Desktop.
    goto :eof
)

REM Verificar se Docker Compose esta instalado
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    docker-compose --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERRO: Docker Compose nao esta instalado. Por favor, instale o Docker Desktop.
        goto :eof
    )
)

REM Parar servicos existentes (se houver)
echo Parando servicos existentes...
docker compose down
if %errorlevel% neq 0 (
    docker-compose down
)

REM Iniciar servicos
echo Iniciando servicos...
docker compose up -d
if %errorlevel% neq 0 (
    docker compose up -d
)

REM Aguardar servicos ficarem prontos
echo Aguardando servicos ficarem prontos (10 segundos)...
timeout /t 10 /nobreak >nul

REM Verificar status dos servicos
echo Status dos servicos:
docker compose ps
if %errorlevel% neq 0 (
    docker-compose ps
)

echo.
echo Servicos iniciados com sucesso!
echo.
echo URLs de acesso:
echo    InfluxDB: http://localhost:8086
echo    Grafana:  http://localhost:3000
echo.
echo Credenciais:
echo    InfluxDB: admin / adminpassword / my-super-secret-auth-token
echo    Grafana:  admin / adminpassword
echo.
echo Para parar os servicos, execute: docker compose down (ou docker-compose down)


