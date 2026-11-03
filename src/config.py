import json
import os
import re
import unicodedata
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
DB_PATH = BASE_DIR / "bric_hunter.db"
CHROME_PROFILE_DIR = BASE_DIR / ".chrome_profile"
LOGS_DIR = BASE_DIR / "logs"

# Garante existência das pastas essenciais
LOGS_DIR.mkdir(exist_ok=True)
CHROME_PROFILE_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    "criterios_arbitragem": {
        "margem_minima_reais": 250,
        "desconto_giro_rapido_reais": 150,
        "desconto_minimo_percentual": 20,
        "aceita_avaria": False
    },
    "localizacao": {
        "cidade": "Fortaleza",
        "raio_km": 50,
        "categoria": "electronics"
    },
    "notificacoes": {
        "telegram_token": "",
        "telegram_chat_id": ""
    },
    "inteligencia_artificial": {
        "gemini_api_key": ""
    },
    "execucao": {
        "intervalo_minutos": 10,
        "ativo": True
    }
}


def normalizar_slug_cidade(cidade: str) -> str:
    """
    Normaliza o nome da cidade para slug amigável do Facebook Marketplace.
    Ex: 'São Paulo' -> 'saopaulo', 'Rio de Janeiro' -> 'rio', 'Belo Horizonte' -> 'belohorizonte'
    """
    if not cidade:
        return "saopaulo"

    cidade_limpa = cidade.strip().lower()

    # Mapeamentos comuns para cidades brasileiras no Marketplace
    apelidos = {
        "sao paulo": "saopaulo",
        "são paulo": "saopaulo",
        "rio de janeiro": "rio",
        "belo horizonte": "belohorizonte",
        "porto alegre": "portoalegre",
        "brasilia": "brasilia",
        "brasília": "brasilia"
    }

    if cidade_limpa in apelidos:
        return apelidos[cidade_limpa]

    # Remove acentos e caracteres especiais
    normalizado = unicodedata.normalize("NFKD", cidade_limpa)
    sem_acentos = "".join(c for c in normalizado if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9]", "", sem_acentos)
    return slug or "saopaulo"


def load_config() -> dict:
    """Carrega o config.json. Cria com valores padrão se não existir."""
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(config_data: dict) -> None:
    """Salva a estrutura de configuração no config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)


def gerar_url_marketplace(cidade: str = "saopaulo", categoria: str = "electronics", raio_km: int = 50) -> str:
    """
    Gera a URL canônica do Facebook Marketplace com ordenação por Mais Recentes.
    """
    slug = normalizar_slug_cidade(cidade)
    cat = categoria or "electronics"
    # O Facebook aceita ordenação por criação decrescente
    return f"https://www.facebook.com/marketplace/{slug}/{cat}?sortBy=creation_time_descend"
