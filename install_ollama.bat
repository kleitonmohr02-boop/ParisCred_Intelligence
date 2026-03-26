@echo off
echo ========================================
echo   INSTALAR OLLAMA
echo ========================================
echo.

echo Baixando Ollama...
curl -kL -o "%TEMP%\OllamaSetup.exe" "https://github.com/ollama/ollama/releases/download/v0.18.2/OllamaSetup.exe"

echo.
echo Instalando Ollama...
"%TEMP%\OllamaSetup.exe" /S

echo.
echo Aguardando Ollama iniciar...
timeout /t 10

echo.
echo Baixando modelo Qwen3-8B (isso pode levar alguns minutos)...
ollama pull qwen3:8b

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para usar: ollama run qwen3:8b
echo.
pause
