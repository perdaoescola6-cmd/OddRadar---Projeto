@echo off
title BetFaro - Inicializador
color 0A

echo ============================================
echo    BetFaro - Inicializador
echo ============================================
echo.

:: Definir diretorio base
set BASE_DIR=C:\Users\Leonardo\OneDrive\Desktop\Windsurf bot test

:: Verificar se o diretorio existe
if not exist "%BASE_DIR%" (
    echo [ERRO] Diretorio nao encontrado: %BASE_DIR%
    pause
    exit /b 1
)

echo [INFO] Diretorio base: %BASE_DIR%
echo.

:: ============================================
:: INICIAR BACKEND
:: ============================================
echo [1/2] Iniciando Backend (FastAPI)...
echo.

:: Abrir nova janela para o backend
start "BetFaro Backend" cmd /k "cd /d %BASE_DIR% && .venv\Scripts\activate && cd backend && echo [BACKEND] Servidor iniciando em http://localhost:8000 && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Aguardar backend iniciar
echo [INFO] Aguardando backend iniciar (5 segundos)...
timeout /t 5 /nobreak >nul

:: ============================================
:: INICIAR FRONTEND
:: ============================================
echo [2/2] Iniciando Frontend (Next.js)...
echo.

:: Abrir nova janela para o frontend
start "BetFaro Frontend" cmd /k "cd /d %BASE_DIR%\frontend && echo [FRONTEND] Servidor iniciando em http://localhost:3000 && npm run dev"

:: ============================================
:: FINALIZADO
:: ============================================
echo.
echo ============================================
echo    BetFaro Iniciado!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Pressione qualquer tecla para abrir o navegador...
pause >nul

:: Abrir navegador
start http://localhost:3000

echo.
echo [INFO] Para encerrar, feche as janelas do Backend e Frontend.
echo.
pause
