@echo off
title BetFaro - Encerrar
color 0C

echo ============================================
echo    BetFaro - Encerrando...
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
echo    BetFaro Encerrado!
echo ============================================
echo.
pause
