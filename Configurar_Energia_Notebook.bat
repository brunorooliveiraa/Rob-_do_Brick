@echo off
title Robo do Brick - Configuracao de Energia do Notebook
cls
echo ========================================================
echo    CONFIGURAR NOTEBOOK PARA RODAR 24/7 DE TAMPA FECHADA
echo ========================================================
echo.
echo Esta opcao ajusta o Windows (apenas quando conectado na tomada) para:
echo   1. NAO suspender nem desligar por inatividade.
echo   2. Continuar rodando normalmente quando voce FECHAR A TAMPA.
echo.
echo Deseja aplicar essa configuracao agora?
echo.
echo [1] Sim, aplicar configuracao para rodar 24/7 (Recomendado)
echo [2] Nao, sair
echo.
set /p OPCAO="Escolha uma opcao [1 ou 2]: "

if "%OPCAO%"=="1" (
    echo.
    echo Aplicando configuracoes no Windows...
    :: Desativa suspensao automatica na tomada (0 = nunca)
    powercfg /change standby-timeout-ac 0
    :: Desativa hibernacao automatica na tomada (0 = nunca)
    powercfg /change hibernate-timeout-ac 0
    :: Configura o fechamento da tampa na tomada para "Nada a Fazer" (0 = Do nothing)
    powercfg /setacvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0
    :: Aplica o plano atual
    powercfg /setactive SCHEME_CURRENT
    echo.
    echo ========================================================
    echo [SUCESSO] Configuracao aplicada!
    echo Agora voce pode fechar a tampa do notebook com ele na
    echo tomada que ele continuara ligado rodando o robo direto!
    echo ========================================================
    echo.
    pause
    exit /b
)

exit /b
