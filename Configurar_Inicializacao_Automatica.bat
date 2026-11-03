@echo off
title Robo do Brick - Inicializacao Automatica com o Windows
cls
echo ========================================================
echo    ROBO DO BRICK - INICIALIZACAO AUTOMATICA COM WINDOWS
echo ========================================================
echo.
echo Este utilitario configura o Robo do Brick para iniciar
echo automaticamente em segundo plano sempre que seu notebook ligar.
echo.
echo [1] Ativar Inicializacao Automatica com o Windows
echo [2] Desativar Inicializacao Automatica
echo [3] Sair
echo.
set /p OPCAO="Escolha uma opcao [1, 2 ou 3]: "

if "%OPCAO%"=="1" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut(\"$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Robo_do_Brick_Segundo_Plano.lnk\"); $Shortcut.TargetPath = \"$PSScriptRoot\Iniciar_Servico_Segundo_Plano.vbs\"; $Shortcut.WorkingDirectory = \"$PSScriptRoot\"; $Shortcut.Save(); Write-Host '`n[SUCESSO] Inicializacao automatica configurada com sucesso!' -ForegroundColor Green"
    echo.
    echo O robo ira iniciar em segundo plano automaticamente ao ligar o notebook.
    echo.
    pause
    exit /b
)

if "%OPCAO%"=="2" (
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Robo_do_Brick_Segundo_Plano.lnk" 2>nul
    echo.
    echo [SUCESSO] Inicializacao automatica removida com sucesso.
    echo.
    pause
    exit /b
)

exit /b
