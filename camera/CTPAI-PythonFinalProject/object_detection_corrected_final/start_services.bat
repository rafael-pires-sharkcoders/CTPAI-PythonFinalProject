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
docker compose down 2>nul
if %errorlevel% neq 0 (
    docker-compose down 2>nul
)

REM Limpar volumes orfaos e redes nao utilizadas
echo Limpando recursos Docker nao utilizados...
docker system prune -f --volumes 2>nul

REM Iniciar servicos
echo Iniciando servicos...
docker compose up -d
if %errorlevel% neq 0 (
    echo Tentando com docker-compose...
    docker-compose up -d
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao iniciar servicos com Docker Compose.
        echo Verifique se o Docker Desktop esta rodando.
        pause
        goto :eof
    )
)

REM Aguardar servicos ficarem prontos
echo Aguardando servicos ficarem prontos (15 segundos)...
timeout /t 15 /nobreak >nul

REM Verificar se InfluxDB esta respondendo
echo Testando conectividade InfluxDB...
curl -s http://localhost:8086/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ InfluxDB esta respondendo
) else (
    echo ⚠️ InfluxDB ainda nao esta pronto, aguarde mais alguns segundos
)

REM Verificar se Grafana esta respondendo
echo Testando conectividade Grafana...
curl -s http://localhost:3000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Grafana esta respondendo
) else (
    echo ⚠️ Grafana ainda nao esta pronto, aguarde mais alguns segundos
)

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


