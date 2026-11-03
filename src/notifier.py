import logging
import requests
from typing import Optional, Tuple, List
from src.config import load_config

logger = logging.getLogger(__name__)


def testar_conexao_telegram(token: str, chat_id: str) -> Tuple[bool, str]:
    """
    Testa se as credenciais do Telegram estão válidas disparando uma mensagem de teste.
    """
    if not token or not chat_id:
        return False, "Token ou Chat ID não preenchidos."

    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🤖 <b>Robô do Brick:</b> Conexão com Telegram validada com sucesso! Sistema de avaliação autônoma ativo.",
        "parse_mode": "HTML"
    }

    try:
        res = requests.post(endpoint, json=payload, timeout=10)
        data = res.json()
        if res.status_code == 200 and data.get("ok"):
            return True, "Mensagem enviada com sucesso ao seu Telegram!"
        return False, data.get("description", "Erro retornado pelo Telegram.")
    except Exception as e:
        return False, f"Falha de conexão com os servidores do Telegram: {e}"


def enviar_alerta_oportunidade(
    marca: str,
    modelo: str,
    especificacoes: Optional[str],
    preco_anunciado: float,
    preco_mercado_medio: float,
    margem_estimada_reais: float,
    margem_percentual: float,
    justificativa: str,
    links_referencia: List[str],
    url_anuncio: str,
    url_imagem: Optional[str] = None,
    avaria: Optional[str] = None,
    preco_venda_rapida: float = 0.0,
    desconto_giro_rapido: float = 0.0,
    descricao_vendedor: Optional[str] = None,
    dados_concorrentes: Optional[dict] = None,
    cidade: str = "Fortaleza"
) -> bool:
    """
    Envia alerta rico no Telegram com foto, preço de giro rápido, dados reais de concorrentes
    no Facebook Marketplace, descrição real do vendedor e botões diretos do Facebook e OLX Ceará.
    """
    config = load_config()
    token = config.get("notificacoes", {}).get("telegram_token")
    chat_id = config.get("notificacoes", {}).get("telegram_chat_id")

    if not token or not chat_id:
        logger.warning("Telegram token ou chat_id não configurados.")
        return False

    status_avaria = f"⚠️ <b>Atenção:</b> {avaria}" if avaria else "✅ <b>Condição:</b> Sem avarias graves"

    desc_curta = ""
    if descricao_vendedor and len(descricao_vendedor.strip()) > 5:
        linhas_desc = [l.strip() for l in descricao_vendedor.strip().split("\n") if l.strip()][:3]
        desc_texto = " ".join(linhas_desc)[:200]
        desc_curta = f"\n📝 <b>Descrição do Vendedor:</b> <i>\"{desc_texto}\"</i>\n"

    # Formata métricas de concorrentes locais no Facebook
    info_mercado = ""
    if dados_concorrentes and dados_concorrentes.get("total_encontrados", 0) > 0:
        total_c = dados_concorrentes["total_encontrados"]
        med_c = dados_concorrentes["preco_medio"]
        min_c = dados_concorrentes.get("preco_min", 0.0)
        info_mercado = f"👥 <b>Concorrentes no Facebook ({cidade}):</b> Média R$ {med_c:,.2f} <i>({total_c} anúncios ativos | menor R$ {min_c:,.2f})</i>\n"
    elif preco_mercado_medio > 0:
        info_mercado = f"📊 <b>Preço Médio Estimado:</b> R$ {preco_mercado_medio:,.2f}\n"

    # Formata links de referência (única e exclusivamente Facebook e OLX Ceará)
    links_texto = ""
    link_olx = ""
    link_fb_busca = ""
    if links_referencia:
        links_texto = "\n🔍 <b>Canais de Validação e Arbitragem:</b>\n"
        for link in links_referencia:
            if "olx.com.br" in link:
                link_olx = link
                links_texto += f"  • <a href=\"{link}\">🛒 OLX Ceará (Fortaleza e Região)</a>\n"
            elif "facebook.com/marketplace" in link:
                link_fb_busca = link
                links_texto += f"  • <a href=\"{link}\">👥 Concorrentes no Facebook ({cidade})</a>\n"
            else:
                links_texto += f"  • <a href=\"{link}\">🔗 Comparar Preço</a>\n"

    info_venda_rapida = ""
    if preco_venda_rapida > 0 and desconto_giro_rapido > 0:
        info_venda_rapida = f"⚡ <b>Preço de Venda Rápida:</b> <b>R$ {preco_venda_rapida:,.2f}</b> (-R$ {desconto_giro_rapido:,.0f} p/ vender em 24h)\n"

    caption = (
        f"🔥 <b>OPORTUNIDADE DE GARIMPO (GIRO RÁPIDO)!</b>\n\n"
        f"📱 <b>Produto:</b> {marca} {modelo} {f'({especificacoes})' if especificacoes else ''}\n\n"
        f"🏷️ <b>Preço Anunciado:</b> R$ {preco_anunciado:,.2f}\n"
        f"{info_mercado}"
        f"{info_venda_rapida}"
        f"💰 <b>Lucro Real Estimado:</b> <b>+ R$ {margem_estimada_reais:,.2f}</b> ({margem_percentual:.0f}% de margem)\n"
        f"{desc_curta}\n"
        f"💡 <i>{justificativa}</i>\n"
        f"{status_avaria}\n"
        f"{links_texto}"
    )

    # Botões interativos no Telegram
    botoes = [
        [{"text": "👉 Abrir Anúncio do Vendedor", "url": url_anuncio}]
    ]
    botoes_linha_2 = []
    if link_olx:
        botoes_linha_2.append({"text": "🛒 Comparar na OLX Ceará", "url": link_olx})
    if link_fb_busca:
        botoes_linha_2.append({"text": "👥 Concorrentes no Facebook", "url": link_fb_busca})

    if botoes_linha_2:
        botoes.append(botoes_linha_2)

    reply_markup = {"inline_keyboard": botoes}

    try:
        if url_imagem and url_imagem.startswith("http"):
            endpoint = f"https://api.telegram.org/bot{token}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "photo": url_imagem,
                "caption": caption,
                "parse_mode": "HTML",
                "reply_markup": reply_markup
            }
        else:
            endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": caption,
                "parse_mode": "HTML",
                "reply_markup": reply_markup,
                "disable_web_page_preview": True
            }

        response = requests.post(endpoint, json=payload, timeout=12)
        return response.status_code == 200 and response.json().get("ok", False)

    except Exception as e:
        logger.error(f"Falha ao enviar alerta no Telegram: {e}")
        return False
