@echo off
chcp 65001 >nul
title Deploy ParisCred - Google Cloud

echo ╔══════════════════════════════════════════════════════════════╗
echo ║       DEPLOY PARISCRED INTELLIGENCE v2.0                    ║
echo ║       Google Cloud Run                                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM VERIFICAR SE GLOUD ESTÁ INSTALADO
REM ============================================================
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Google Cloud SDK não está instalado!
    echo.
    echo Para instalar, abra o PowerShell como Administrador e execute:
    echo   choco install google-cloud-sdk
    echo.
    echo Ou baixe manualmente em: https://cloud.google.com/sdk/docs/install
    echo.
    pause
    exit /b 1
)

echo [1/7] Google Cloud SDK encontrado!

REM ============================================================
REM AUTENTICAR
REM ============================================================
echo.
echo [2/7] Fazendo login no Google Cloud...
gcloud auth login --brief

REM ============================================================
REM PEDIR ID DO PROJETO
REM ============================================================
echo.
echo [3/7] Configurando projeto...
echo.
echo Digite o ID do seu projeto Google Cloud:
echo (Se não tem, crie em: https://console.cloud.google.com/projectcreate)
set /p PROJECT_ID=

if "%PROJECT_ID%"=="" (
    echo [ERRO] Projeto não especificado!
    pause
    exit /b 1
)

gcloud config set project %PROJECT_ID%

REM ============================================================
REM ATIVAR APIS
REM ============================================================
echo.
echo [4/7] Ativando APIs do Google Cloud...
echo (Isso pode levar alguns minutos)

gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet

echo [OK] APIs ativadas!

REM ============================================================
REM DEPLOY
REM ============================================================
echo.
echo [5/7] Fazendo deploy no Google Cloud Run...
echo (Este processo pode levar 5-15 minutos na primeira vez)
echo.

gcloud run deploy pariscred-app ^
    --source . ^
    --platform managed ^
    --region us-central1 ^
    --allow-unauthenticated ^
    --memory 1Gi ^
    --cpu 1 ^
    --timeout 900 ^
    --set-env-vars "FLASK_ENV=production,DATABASE_PATH=/tmp/pariscred.db"

if %errorlevel% neq 0 (
    echo [ERRO] O deploy falhou!
    pause
    exit /b 1
)

REM ============================================================
REM OBTER URL
REM ============================================================
echo.
echo [6/7] Obtendo URL do serviço...

for /f "delims=" %%i in ('gcloud run services describe pariscred-app --platform managed --region us-central1 --format ^"value(status.url)^"') do set SERVICE_URL=%%i

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  ✓ DEPLOY CONCLUÍDO COM SUCESSO!                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🌐 SEU SISTEMA ESTÁ ONLINE:
echo    %SERVICE_URL%
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📋 INFORMAÇÕES DE ACESSO:
echo    Email:    admin@pariscred.com
echo    Senha:    Admin@2025
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo ⚠️  PRÓXIMOS PASSOS:
echo    1. Acesse o link acima e faça login
echo    2. Para WhatsApp funcionar, configure a Evolution API
echo    3. A variável EVOLUTION_API_URL precisa apontar para sua API
echo.

REM Salvar URL em arquivo
echo %SERVICE_URL% > DEPLOY_URL.txt

echo [OK] URL salva em DEPLOY_URL.txt

echo.
pause