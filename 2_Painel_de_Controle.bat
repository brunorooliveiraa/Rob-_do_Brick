@echo off
title Robo do Brick - Painel de Controle
cls
echo ========================================================
echo    ROBO DO BRICK - PAINEL DE CONTROLE LOCAL
echo ========================================================
echo.
echo Iniciando o Dashboard em http://localhost:5000 ...
echo Seu navegador sera aberto automaticamente em instantes.
echo.
echo Para fechar o painel, feche esta janela ou pressione CTRL+C.
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" dashboard.py
) else (
    python dashboard.py
)

pause
