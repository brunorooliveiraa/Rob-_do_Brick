import sys
import os
import time
import logging
from datetime import datetime, timedelta

# Suporte a UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import LOGS_DIR
from main import executar_ciclo_garimpo

# Configuração de Log
log_file = LOGS_DIR / "bric_hunter.log"
handlers = [logging.FileHandler(log_file, encoding="utf-8")]
if sys.stdout is not None:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=handlers
)
logger = logging.getLogger("ServicoGarimpo")

# Trava de instância única para evitar duas instâncias concorrentes
LOCK_FILE = LOGS_DIR / "servico_garimpo.lock"


def adquirir_trava() -> bool:
    """Garante que apenas uma instância do serviço esteja rodando."""
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            # Verifica se o processo com esse PID ainda existe no Windows
            import ctypes
            kernel32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x00100000
            process = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
            if process != 0:
                kernel32.CloseHandle(process)
                return False  # Processo ainda ativo
        except Exception:
            pass  # PID antigo ou inválido

    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        return True
    except Exception:
        return False


def liberar_trava() -> None:
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def obter_intervalo_segundos() -> tuple[int, str]:
    """
    Retorna o intervalo de espera baseado na hora do dia:
    - Madrugada (00:00 às 04:59): a cada 2 horas (7200s)
    - Dia/Noite (05:00 às 23:59): a cada 15 minutos (900s)
    """
    hora_atual = datetime.now().hour
    if 0 <= hora_atual < 5:
        return 2 * 3600, "2 horas (Horário de Madrugada)"
    else:
        return 15 * 60, "15 minutos (Horário Diurno/Comercial)"


def garantir_conexao_internet(tentativas: int = 3) -> bool:
    """Verifica se há conexão com a internet; se não houver, força reconexão automática do Wi-Fi."""
    import socket
    import subprocess
    for t in range(tentativas):
        try:
            s = socket.create_connection(("8.8.8.8", 53), timeout=3)
            s.close()
            return True
        except Exception:
            logger.warning(f"Wi-Fi offline ou instável ao fechar a tampa. Forçando reconexão imediata (tentativa {t+1}/{tentativas})...")
            try:
                subprocess.run(["netsh", "wlan", "connect", "name=MOB AP204"], capture_output=True, timeout=5)
            except Exception:
                pass
            time.sleep(4)
    return False


def loop_servico() -> None:
    if not adquirir_trava():
        logger.warning("O Serviço do Robô do Brick já está em execução em segundo plano. Encerrando duplicata.")
        sys.exit(0)

    logger.info("=" * 60)
    logger.info("🚀 SERVIÇO EM SEGUNDO PLANO INICIADO COM SUCESSO!")
    logger.info("⏰ Cronograma inteligente:")
    logger.info("   • 05:00 às 00:00: Varredura a cada 15 minutos")
    logger.info("   • 00:00 às 05:00: Varredura a cada 2 horas (Madrugada)")
    logger.info("=" * 60)

    try:
        while True:
            # Blindagem: garante internet ativa antes de iniciar a raspagem
            garantir_conexao_internet()

            logger.info("Executando ciclo programado de garimpo...")
            try:
                executar_ciclo_garimpo()
            except Exception as e:
                logger.error(f"Erro durante o ciclo de garimpo: {e}", exc_info=True)

            segundos, descricao = obter_intervalo_segundos()
            proxima_execucao = datetime.now() + timedelta(seconds=segundos)
            logger.info(
                f"Ciclo concluído. Próxima varredura programada para {proxima_execucao.strftime('%H:%M:%S')} "
                f"(Intervalo: {descricao})."
            )

            # Grava na telemetria do ciclo para visualização imediata no Dashboard
            try:
                from src.database import carregar_telemetria_ciclo, salvar_telemetria_ciclo
                tele = carregar_telemetria_ciclo()
                tele["proxima_execucao"] = proxima_execucao.strftime("%H:%M:%S")
                tele["intervalo_descricao"] = descricao
                tele["intervalo_segundos"] = segundos
                salvar_telemetria_ciclo(tele)
            except Exception:
                pass

            # Aguarda o intervalo de tempo
            time.sleep(segundos)

    except (KeyboardInterrupt, SystemExit):
        logger.info("Serviço finalizado pelo usuário ou sistema.")
    finally:
        liberar_trava()


if __name__ == "__main__":
    loop_servico()
