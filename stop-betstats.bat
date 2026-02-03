@echo off
title BetStats Trader - Encerrar
color 0C

echo ============================================
echo    BetStats Trader - Encerrando...
echo ============================================
echo.

:: Encerrar processos Node (Frontend)
echo [1/2] Encerrando Frontend (Node.js)...
taskkill /F /IM node.exe >nul 2>&1

:: Encerrar processos Python (Backend)
echo [2/2] Encerrando Backend (Python)...
taskkill /F /IM python.exe >nul 2>&1

echo.
echo ============================================
echo    BetStats Trader Encerrado!
echo ============================================
echo.
pause
