import sys
import os
import re
import time
import subprocess
import signal
from pathlib import Path

# Suporte a UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.config import LOGS_DIR
URL_FILE = LOGS_DIR / "url_publica.txt"


def limpar_url():
    try:
        if URL_FILE.exists():
            URL_FILE.unlink()
    except Exception:
        pass


def main():
    print("=" * 65)
    print("🌐 ROBÔ DO BRICK - ACESSO EXTERNO (FORA DO WI-FI / 4G / 5G)")
    print("=" * 65)
    print("Iniciando túnel seguro de alta velocidade via Cloudflare...")
    print("Aguarde alguns segundos...\n")

    cloudflared_path = Path("cloudflared.exe")
    if not cloudflared_path.exists():
        print("❌ Erro: cloudflared.exe não encontrado na pasta do projeto.")
        input("\nPressione Enter para sair...")
        return

    cmd = [str(cloudflared_path.resolve()), "tunnel", "--url", "http://localhost:5000"]

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            bufsize=1
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar cloudflared: {e}")
        input("\nPressione Enter para sair...")
        return

    url_publica = None
    inicio = time.time()

    # Lê o log do cloudflared procurando a URL pública HTTPS
    for line in iter(proc.stdout.readline, ""):
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            url_publica = match.group(0)
            break
        if time.time() - inicio > 30:
            break

    if not url_publica:
        print("❌ Não foi possível obter o link do túnel em 30 segundos.")
        print("Verifique sua conexão com a internet.")
        proc.terminate()
        input("\nPressione Enter para sair...")
        return

    # Grava a URL no arquivo de status
    try:
        URL_FILE.write_text(url_publica, encoding="utf-8")
    except Exception:
        pass

    print("=" * 65)
    print("🎉 SEU DASHBOARD ESTÁ ACESSÍVEL DE QUALQUER LUGAR DO MUNDO!")
    print("=" * 65)
    print(f"\n👉 LINK HTTPS SEGURO:  {url_publica}\n")
    print("📱 Você pode abrir esse link no seu celular conectado ao 4G/5G,")
    print("   no trabalho ou em qualquer outro lugar fora de casa!")
    print("🔒 Conexão criptografada (HTTPS) 100% gratuita via Cloudflare.")
    print("=" * 65)
    print("\n⚠️ IMPORTANTE: Mantenha esta janela aberta enquanto quiser acessar")
    print("   fora de casa. Para encerrar o acesso externo, aperte CTRL+C ou feche esta janela.\n")

    try:
        while True:
            time.sleep(1)
            if proc.poll() is not None:
                print("O túnel foi encerrado.")
                break
    except KeyboardInterrupt:
        print("\nEncerrando túnel externo...")
    finally:
        limpar_url()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        print("Acesso externo finalizado com sucesso.")


if __name__ == "__main__":
    limpar_url()
    try:
        main()
    finally:
        limpar_url()
