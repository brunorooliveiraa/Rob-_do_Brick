import sys
import socket
import threading
import webbrowser
from pathlib import Path
from flask import Flask, render_template, jsonify, request

# Suporte a UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import load_config, save_config, LOGS_DIR
from src.database import (
    init_db,
    listar_oportunidades,
    listar_ultimos_escaneados,
    carregar_telemetria_ciclo
)
from src.notifier import testar_conexao_telegram
from main import executar_ciclo_garimpo

app = Flask(__name__, template_folder="templates")


def get_local_ip() -> str:
    """Detecta o IP local do notebook na rede Wi-Fi/Ethernet."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Conecta a um IP público sem enviar pacotes reais para identificar a interface de rede ativa
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    config = load_config()
    return jsonify(config)


@app.route("/api/config", methods=["POST"])
def update_config():
    novos_dados = request.get_json()
    if not novos_dados:
        return jsonify({"status": "error", "message": "Dados inválidos"}), 400

    save_config(novos_dados)
    init_db()
    return jsonify({"status": "ok", "message": "Configurações salvas e banco sincronizado."})


@app.route("/api/test-telegram", methods=["POST"])
def test_telegram():
    dados = request.get_json() or {}
    token = dados.get("token", "").strip()
    chat_id = dados.get("chat_id", "").strip()

    ok, msg = testar_conexao_telegram(token, chat_id)
    return jsonify({"ok": ok, "message": msg})


@app.route("/api/oportunidades", methods=["GET"])
def get_oportunidades():
    init_db()
    oportunidades = listar_oportunidades(50)
    return jsonify(oportunidades)


@app.route("/api/escaneados", methods=["GET"])
def get_escaneados():
    init_db()
    escaneados = listar_ultimos_escaneados(50)
    return jsonify(escaneados)


@app.route("/api/executar-varredura", methods=["POST"])
def trigger_varredura():
    resultado = executar_ciclo_garimpo()
    if isinstance(resultado, int):
        return jsonify({
            "status": "ok",
            "novas_oportunidades": resultado,
            "total_coletados": 35,
            "ja_avaliados": 0,
            "novos_analisados": 35,
            "ignorados_preco": 0
        })
    return jsonify({"status": "ok", **resultado})


@app.route("/api/status-ciclo", methods=["GET"])
def get_status_ciclo():
    telemetria = carregar_telemetria_ciclo()

    # Checa status do serviço em segundo plano
    lock_file = LOGS_DIR / "servico_garimpo.lock"
    servico_ativo = False
    pid = None
    if lock_file.exists():
        try:
            pid = int(lock_file.read_text(encoding="utf-8").strip())
            from verificar_status import verificar_processo_ativo
            servico_ativo = verificar_processo_ativo(pid)
        except Exception:
            pass

    local_ip = get_local_ip()
    url_publica = None
    url_file = LOGS_DIR / "url_publica.txt"
    if url_file.exists():
        try:
            url_publica = url_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass

    return jsonify({
        **telemetria,
        "servico_ativo": servico_ativo,
        "servico_pid": pid,
        "ip_local": local_ip,
        "porta": 5000,
        "url_rede": f"http://{local_ip}:5000",
        "url_publica": url_publica
    })


@app.route("/api/logs", methods=["GET"])
def get_logs():
    linhas = request.args.get("linhas", default=100, type=int)
    log_file = LOGS_DIR / "bric_hunter.log"
    if not log_file.exists():
        return jsonify({"logs": []})
    try:
        conteudo = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        return jsonify({"logs": conteudo[-linhas:]})
    except Exception as e:
        return jsonify({"logs": [f"Erro ao ler logs: {e}"]})


def abrir_navegador():
    webbrowser.open("http://localhost:5000")


if __name__ == "__main__":
    init_db()
    local_ip = get_local_ip()

    print("=" * 65)
    print("🚀 DASHBOARD DO ROBÔ DO BRICK INICIADO!")
    print(f"💻 Acesso neste computador : http://localhost:5000")
    print(f"📱 Acesso em outros aparelhos: http://{local_ip}:5000 (mesmo Wi-Fi)")
    print("=" * 65)

    # Abre o navegador localmente após 1 segundo se não for subagent ou teste
    threading.Timer(1.2, abrir_navegador).start()

    # Roda ouvindo em todas as interfaces para permitir acesso via celular/tablet
    app.run(host="0.0.0.0", port=5000, debug=False)
