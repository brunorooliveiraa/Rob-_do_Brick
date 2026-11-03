import shutil
from pathlib import Path

log_path = Path("logs/bric_hunter.log")
bak_path = Path("logs/bric_hunter_anterior.log")

if log_path.exists():
    shutil.copy(log_path, bak_path)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("2026-10-07 17:10:00 [INFO] === SISTEMA REINICIADO COM GEMINI 3.8 FLASH E RE-BUSCA LOCAL ===\n")
        f.write("2026-10-07 17:10:00 [INFO] Monitoramento ativo para Fortaleza e Ceará.\n")

print("Logs rotacionados e limpos com sucesso!")
