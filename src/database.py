import json
import sqlite3
import logging
from typing import Optional, List, Dict, Any
from src.config import DB_PATH, load_config

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Inicializa as tabelas do banco SQLite e cria os índices essenciais."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript("""
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;

            CREATE TABLE IF NOT EXISTS tabela_processados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_anuncio TEXT UNIQUE NOT NULL,
                id_externo TEXT,
                titulo_bruto TEXT NOT NULL,
                preco_anunciado REAL NOT NULL,
                preco_mercado_medio REAL DEFAULT 0.0,
                margem_estimada_reais REAL DEFAULT 0.0,
                margem_percentual REAL DEFAULT 0.0,
                url_imagem TEXT,
                marca_detectada TEXT,
                modelo_detectado TEXT,
                especificacoes TEXT,
                condicao TEXT,
                tem_avaria INTEGER DEFAULT 0,
                descricao_avaria TEXT,
                justificativa TEXT,
                links_referencia TEXT,
                eh_oportunidade INTEGER DEFAULT 0,
                notificado INTEGER DEFAULT 0,
                descricao_anuncio TEXT,
                preco_venda_rapida REAL DEFAULT 0.0,
                desconto_giro_rapido REAL DEFAULT 0.0,
                data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_processados_url 
            ON tabela_processados(url_anuncio);

            CREATE INDEX IF NOT EXISTS idx_processados_data 
            ON tabela_processados(data_processamento);
        """)

        # Garante migração de colunas caso tabela já existisse
        colunas_necessarias = {
            "preco_mercado_medio": "REAL DEFAULT 0.0",
            "margem_estimada_reais": "REAL DEFAULT 0.0",
            "margem_percentual": "REAL DEFAULT 0.0",
            "especificacoes": "TEXT",
            "justificativa": "TEXT",
            "links_referencia": "TEXT",
            "descricao_anuncio": "TEXT",
            "preco_venda_rapida": "REAL DEFAULT 0.0",
            "desconto_giro_rapido": "REAL DEFAULT 0.0",
            "tempo_anuncio": "TEXT",
            "total_concorrentes_facebook": "INTEGER DEFAULT 0",
            "preco_min_facebook": "REAL DEFAULT 0.0",
            "preco_max_facebook": "REAL DEFAULT 0.0",
            "termo_busca_otimizado": "TEXT"
        }
        cursor.execute("PRAGMA table_info(tabela_processados)")
        colunas_existentes = {row["name"] for row in cursor.fetchall()}

        for col, tipo in colunas_necessarias.items():
            if col not in colunas_existentes:
                cursor.execute(f"ALTER TABLE tabela_processados ADD COLUMN {col} {tipo}")

        conn.commit()
    logger.info("Banco de dados SQLite inicializado com suporte a precificação autônoma e giro rápido.")


def is_anuncio_processado(url_anuncio: str) -> bool:
    """Verifica em O(1) se a URL já existe no banco de dados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM tabela_processados WHERE url_anuncio = ? LIMIT 1", (url_anuncio,))
        return cursor.fetchone() is not None


def registrar_anuncio(
    url_anuncio: str,
    titulo_bruto: str,
    preco_anunciado: float,
    url_imagem: Optional[str] = None,
    id_externo: Optional[str] = None,
    dados_avaliacao: Optional[Dict[str, Any]] = None,
    eh_oportunidade: bool = False,
    notificado: bool = False,
    descricao_anuncio: Optional[str] = None,
    preco_venda_rapida: float = 0.0,
    desconto_giro_rapido: float = 0.0,
    tempo_anuncio: Optional[str] = None
) -> None:
    """Registra o anúncio e o parecer de mercado no histórico."""
    marca = dados_avaliacao.get("marca") if dados_avaliacao else None
    modelo = dados_avaliacao.get("modelo") if dados_avaliacao else None
    specs = dados_avaliacao.get("especificacoes") if dados_avaliacao else None
    condicao = dados_avaliacao.get("condicao") if dados_avaliacao else None
    tem_avaria = 1 if (dados_avaliacao and dados_avaliacao.get("tem_avaria")) else 0
    descricao_avaria = dados_avaliacao.get("descricao_avaria") if dados_avaliacao else None

    preco_mercado = float(dados_avaliacao.get("preco_mercado_medio") or 0.0) if dados_avaliacao else 0.0
    margem_reais = float(dados_avaliacao.get("margem_estimada_reais") or 0.0) if dados_avaliacao else 0.0
    margem_pct = float(dados_avaliacao.get("margem_percentual") or 0.0) if dados_avaliacao else 0.0
    justificativa = dados_avaliacao.get("justificativa") if dados_avaliacao else None
    links_ref = json.dumps(dados_avaliacao.get("links_referencia", [])) if dados_avaliacao else "[]"

    # Dados de re-busca no Facebook Marketplace
    total_concorrentes = int(dados_avaliacao.get("total_concorrentes_facebook", 0)) if dados_avaliacao else 0
    preco_min_fb = float(dados_avaliacao.get("preco_min_facebook", 0.0)) if dados_avaliacao else 0.0
    preco_max_fb = float(dados_avaliacao.get("preco_max_facebook", 0.0)) if dados_avaliacao else 0.0
    termo_busca = dados_avaliacao.get("termo_busca_otimizado", "") if dados_avaliacao else ""

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO tabela_processados (
                url_anuncio, id_externo, titulo_bruto, preco_anunciado,
                preco_mercado_medio, margem_estimada_reais, margem_percentual,
                url_imagem, marca_detectada, modelo_detectado, especificacoes,
                condicao, tem_avaria, descricao_avaria, justificativa,
                links_referencia, eh_oportunidade, notificado,
                descricao_anuncio, preco_venda_rapida, desconto_giro_rapido,
                tempo_anuncio, total_concorrentes_facebook, preco_min_facebook,
                preco_max_facebook, termo_busca_otimizado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            url_anuncio, id_externo, titulo_bruto, preco_anunciado,
            preco_mercado, margem_reais, margem_pct,
            url_imagem, marca, modelo, specs,
            condicao, tem_avaria, descricao_avaria, justificativa,
            links_ref, 1 if eh_oportunidade else 0, 1 if notificado else 0,
            descricao_anuncio, preco_venda_rapida, desconto_giro_rapido,
            tempo_anuncio, total_concorrentes, preco_min_fb, preco_max_fb, termo_busca
        ))
        conn.commit()


def salvar_telemetria_ciclo(dados: Dict[str, Any]) -> None:
    """Salva as estatísticas detalhadas do último ciclo de garimpo em arquivo JSON."""
    from src.config import LOGS_DIR
    telemetria_file = LOGS_DIR / "ultimo_ciclo.json"
    try:
        with open(telemetria_file, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.debug(f"Erro ao salvar telemetria do ciclo: {e}")


def carregar_telemetria_ciclo() -> Dict[str, Any]:
    """Carrega as estatísticas do último ciclo de garimpo."""
    from src.config import LOGS_DIR
    telemetria_file = LOGS_DIR / "ultimo_ciclo.json"
    if telemetria_file.exists():
        try:
            with open(telemetria_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def listar_oportunidades(limite: int = 50) -> List[Dict[str, Any]]:
    """Retorna as oportunidades mais recentes para exibição no Dashboard."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tabela_processados 
            WHERE eh_oportunidade = 1 
            ORDER BY data_processamento DESC 
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in cursor.fetchall()]


def listar_ultimos_escaneados(limite: int = 50) -> List[Dict[str, Any]]:
    """Retorna todos os anúncios escaneados recentemente (oportunidades ou não)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tabela_processados 
            ORDER BY data_processamento DESC 
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in cursor.fetchall()]
