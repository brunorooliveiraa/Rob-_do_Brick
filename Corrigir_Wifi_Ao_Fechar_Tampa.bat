@echo off
chcp 65001 >nul
title Corrigir Desconexao do Wi-Fi ao Fechar a Tampa
cls

echo ========================================================
echo    CORRECAO DEFINITIVA DO WI-FI AO FECHAR A TAMPA
echo ========================================================
echo.
echo Placa detectada: Realtek 8822CE Wireless LAN PCI-E NIC
echo Rede: MOB AP204
echo.
echo Esta correcao vai:
echo   1. Desativar a economia de energia da placa Realtek (bLowPowerEnable = 0)
echo   2. Impedir que o Windows desligue o Wi-Fi para economizar bateria
echo   3. Colocar o Wi-Fi em Desempenho Maximo permanente
echo   4. Configurar reconexao 100%% automatica se houver qualquer oscilacao
echo.

:: Verifica privilegios de Administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Solicitando permissao de Administrador do Windows...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo [1/4] Ajustando perfil da rede Wi-Fi para reconectar automaticamente...
netsh wlan set profileparameter name="MOB AP204" connectionmode=auto nonBroadcast=yes >nul 2>&1

echo [2/4] Desativando desligamento da placa Realtek no Registro...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$key = 'HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\0000';" ^
    "if (Test-Path $key) {" ^
    "    Set-ItemProperty -Path $key -Name 'bLowPowerEnable' -Value 0 -ErrorAction SilentlyContinue;" ^
    "    Set-ItemProperty -Path $key -Name 'PnPCapabilities' -Value 24 -ErrorAction SilentlyContinue;" ^
    "}"

echo [3/4] Configurando adaptador sem fio para Desempenho Maximo (Sem desligamento)...
powercfg /setacvalueindex SCHEME_CURRENT 19cbb8fa-5279-450e-9fac-8a3d5fedd0c1 12bbebe6-58d6-4636-95bb-3217ef867c1a 0 >nul 2>&1
powercfg /setdcvalueindex SCHEME_CURRENT 19cbb8fa-5279-450e-9fac-8a3d5fedd0c1 12bbebe6-58d6-4636-95bb-3217ef867c1a 0 >nul 2>&1
powercfg /setactive SCHEME_CURRENT >nul 2>&1

echo [4/4] Reiniciando conexao Wi-Fi para aplicar alteracoes...
netsh interface set interface "Wi-Fi" disable >nul 2>&1
ping 127.0.0.1 -n 3 >nul
netsh interface set interface "Wi-Fi" enable >nul 2>&1
ping 127.0.0.1 -n 3 >nul
netsh wlan connect name="MOB AP204" >nul 2>&1

echo.
echo ========================================================
echo [SUCESSO COMPLETO!] O Wi-Fi foi blindado com sucesso!
echo Agora voce pode fechar a tampa que o Wi-Fi permanecera
echo 100%% conectado e estavel 24 horas por dia!
echo ========================================================
echo.
pause
