@echo off
title Robo do Brick - Conectar Facebook
cls
echo ========================================================
echo    ROBO DO BRICK - CONEXAO DO FACEBOOK
echo ========================================================
echo.
echo Iniciando o navegador para autenticacao...
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" login_helper.py
) else (
    python login_helper.py
)

echo.
pause
