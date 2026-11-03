@echo off
chcp 65001 >nul
title Robo do Brick - Central de Execucao
cls

:menu
cls
echo ========================================================
echo    ROBO DO BRICK - CENTRAL DE EXECUCAO E MONITORAMENTO
echo ========================================================
echo.
echo Selecione a opcao desejada:
echo.
echo [1] Iniciar em SEGUNDO PLANO (100%% Invisivel)
echo     - Roda a cada 15 min (05:00 as 00:00)
echo     - Roda a cada 2 horas de madrugada (00:00 as 05:00)
echo.
echo [2] Rodar 1 Varredura Agora (Visivel no terminal para teste)
echo.
echo [3] Verificar Status / Ultimos Alertas no Log
echo.
echo [4] Parar Robo em Segundo Plano
echo.
echo [5] Compartilhar na Internet (Acesso 4G/5G Fora de Casa)
echo.
echo [6] Sair
echo.
choice /c 123456 /n /m "Digite o numero da opcao [1 a 6]: "
if errorlevel 6 goto sair
if errorlevel 5 goto compartilhar_internet
if errorlevel 4 goto parar_robo
if errorlevel 3 goto ver_status
if errorlevel 2 goto rodar_agora
if errorlevel 1 goto iniciar_fundo
goto menu

:iniciar_fundo
echo.
echo Iniciando o servico invisivel em segundo plano...
wscript.exe Iniciar_Servico_Segundo_Plano.vbs
echo.
echo [SUCESSO] Robo iniciado em segundo plano!
echo Ele continuara garimpando silenciosamente e enviando alertas no Telegram.
echo.
pause
goto menu

:rodar_agora
echo.
echo Executando varredura imediata...
echo.
if exist .venv\Scripts\python.exe (
    call .venv\Scripts\python.exe main.py
) else (
    call python main.py
)
echo.
echo Varredura finalizada!
echo.
pause
goto menu

:ver_status
cls
if exist .venv\Scripts\python.exe (
    call .venv\Scripts\python.exe verificar_status.py
) else (
    call python verificar_status.py
)
echo.
pause
goto menu

:parar_robo
call Parar_Servico.bat
goto menu

:compartilhar_internet
call Compartilhar_Na_Internet.bat
goto menu

:sair
exit /b
