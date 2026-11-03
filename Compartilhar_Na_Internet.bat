@echo off
chcp 65001 >nul
title Robo do Brick - Acesso Fora de Casa (4G / 5G)
cls

if exist .venv\Scripts\python.exe (
    call .venv\Scripts\python.exe compartilhar_internet.py
) else (
    call python compartilhar_internet.py
)

pause
