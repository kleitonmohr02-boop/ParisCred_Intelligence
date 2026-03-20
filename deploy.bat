@echo off
REM ==========================================================
REM Deploy Script para ParisCred Intelligence no Render.com
REM ==========================================================

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo   DEPLOY PARISCRED INTELLIGENCE
echo ======================================================================
echo.

REM Verificar se git está instalado
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Git não está instalado!
    echo    Instale em https://git-scm.com
    pause
    exit /b 1
)

echo [1] Preparando repositório Git...
git init
if %errorlevel% neq 0 echo ⚠️  Já é um repositório git existente

echo [2] Adicionando arquivos...
git add .
git commit -m "Deploy ParisCred Intelligence - Sistema Completo"

echo.
echo [3] Próximos passos:
echo.
echo    A. Criar repositório no GitHub:
echo       1. Ir para https://github.com/new
echo       2. Nome: pariscred-intelligence
echo       3. Copiar o URL do repositório
echo.
echo    B. Conectar e fazer push:
echo       git remote add origin [URL_DO_REPO]
echo       git branch -M main
echo       git push -u origin main
echo.
echo    C. Deploy no Render.com:
echo       1. Ir para https://render.com
echo       2. Fazer login com GitHub
echo       3. Clicar em "New Web Service"
echo       4. Conectar repositório pariscred-intelligence
echo       5. Configurar como indicado em DEPLOY_GUIDE.md
echo.
echo ======================================================================
echo   Sistema pronto para deploy! 🚀
echo ======================================================================
echo.
pause
