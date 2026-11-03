@echo off
chcp 65001 >nul
title Robo do Brick - Parar Servico em Segundo Plano
cls
echo ========================================================
echo    ROBO DO BRICK - ENCERRANDO SERVICO EM SEGUNDO PLANO
echo ========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$lock = 'logs\servico_garimpo.lock';" ^
    "if (Test-Path $lock) {" ^
    "    $pidVal = (Get-Content $lock).Trim();" ^
    "    Stop-Process -Id $pidVal -Force -ErrorAction SilentlyContinue;" ^
    "    Remove-Item $lock -Force -ErrorAction SilentlyContinue;" ^
    "    Write-Host ('[SUCESSO] O servico do Robo do Brick (PID ' + $pidVal + ') foi encerrado.') -ForegroundColor Green;" ^
    "} else {" ^
    "    Get-Process pythonw -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*servico_garimpo*' } | Stop-Process -Force -ErrorAction SilentlyContinue;" ^
    "    Write-Host '[INFO] Nenhum servico ativo detectado.' -ForegroundColor Yellow;" ^
    "}"
echo.
pause
