import sys
import os
from pathlib import Path

# Garante suporte a UTF-8 e caracteres acentuados no CMD do Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

LOCK_FILE = Path("logs/servico_garimpo.lock")
LOG_FILE = Path("logs/bric_hunter.log")

def verificar_processo_ativo(pid: int) -> bool:
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x00100000
        process = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
        if process != 0:
            kernel32.CloseHandle(process)
            return True
    except Exception:
        pass
    return False

def main():
    print("=" * 65)
    print("           ROBO DO BRICK - STATUS DO SERVICO")
    print("=" * 65)

    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text(encoding="utf-8").strip())
            if verificar_processo_ativo(pid):
                print(f"[STATUS: ATIVO] O robo esta RODANDO em segundo plano!")
                print(f"PID do processo: {pid}")
                print("Modo: Silencioso / Segundo Plano (pythonw)")
                print("Rotina: 15 min (05:00 as 00:00) | 2 horas (00:00 as 05:00)")
            else:
                print(f"[STATUS: PARADO] O robo nao esta em execucao no momento.")
                print(f"(A trava anterior continha PID {pid}, mas o processo ja finalizou)")
        except Exception as e:
            print(f"[STATUS: INDETERMINADO] Erro ao ler trava: {e}")
    else:
        print("[STATUS: PARADO] O robo nao esta em execucao em segundo plano.")
        print("Para iniciar, escolha a opcao [1] no menu principal.")

    def obter_ip_local():
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    ip = obter_ip_local()
    print(f"\n📱 Painel Web no Celular: http://{ip}:5000 (mesmo Wi-Fi)")

    try:
        from src.database import carregar_telemetria_ciclo
        tele = carregar_telemetria_ciclo()
        if tele:
            print("\n" + "=" * 65)
            print("         TELEMETRIA DA ULTIMA CAPTURA")
            print("=" * 65)
            print(f"Ultima captura: {tele.get('timestamp_formatado', '--')}")
            print(f"Total coletados: {tele.get('total_coletados', 0)} anúncios")
            print(f"Ja avaliados (repetidos): {tele.get('repetidos', 0)}")
            print(f"Ignorados (Preco R$ 0 / Gratis): {tele.get('ignorados_preco', 0)}")
            print(f"Novos analisados pela IA: {tele.get('novos_analisados', 0)}")
            print(f"Oportunidades encontradas: {tele.get('novas_oportunidades', 0)}")
            print(f"Proxima varredura: {tele.get('proxima_execucao', '--')} ({tele.get('intervalo_descricao', '--')})")
    except Exception:
        pass

    print("\n" + "=" * 65)
    print("            ULTIMAS LINHAS DO REGISTRO (LOG)")
    print("=" * 65)

    if LOG_FILE.exists():
        try:
            lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
            ultimas = lines[-15:]
            for linha in ultimas:
                print(linha)
        except Exception as e:
            print(f"Erro ao ler arquivo de log: {e}")
    else:
        print("Arquivo de log ainda nao existe.")

    print("=" * 65)

if __name__ == "__main__":
    main()
