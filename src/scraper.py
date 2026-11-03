import re
import sys
import time
import logging
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, BrowserContext, Page

from src.config import (
    load_config,
    gerar_url_marketplace,
    CHROME_PROFILE_DIR
)

# Configura encoding UTF-8 para ambiente Windows se necessário
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger(__name__)


def sanitizar_preco(texto_preco: str) -> float:
    """
    Converte strings de preço como 'R$ 1.250', 'R$ 800,00', 'US$75', 'Grátis' em float.
    """
    if not texto_preco:
        return 0.0

    texto = texto_preco.strip().lower()
    if "grátis" in texto or "gratis" in texto or "free" in texto:
        return 0.0

    # Remove símbolos de moeda e texto irrelevante, mantendo dígitos, pontos e vírgulas
    numeros = re.sub(r"[^\d,\.]", "", texto)
    if not numeros:
        return 0.0

    # Formato brasileiro com vírgula decimal (ex: 1.500,00)
    if "," in numeros and "." in numeros:
        numeros = numeros.replace(".", "").replace(",", ".")
    elif "," in numeros:
        numeros = numeros.replace(",", ".")
    elif "." in numeros:
        # Se tiver mais de 2 dígitos após o ponto, era separador de milhar (ex: 1.500)
        partes = numeros.split(".")
        if len(partes[-1]) == 3:
            numeros = "".join(partes)

    try:
        return float(numeros)
    except ValueError:
        return 0.0


def normalizar_url_item(url_bruta: str) -> str:
    """
    Remove parâmetros de rastreamento do Facebook e retorna a URL canônica do anúncio.
    Exemplo: /marketplace/item/1234567890/?ref=search -> https://www.facebook.com/marketplace/item/1234567890/
    """
    if not url_bruta.startswith("http"):
        url_bruta = f"https://www.facebook.com{url_bruta}"

    match = re.search(r"marketplace/item/(\d+)", url_bruta)
    if match:
        item_id = match.group(1)
        return f"https://www.facebook.com/marketplace/item/{item_id}/"
    return url_bruta.split("?")[0]


def extrair_id_item(url_bruta: str) -> Optional[str]:
    """
    Extrai o ID numérico do anúncio do Marketplace a partir da URL.
    """
    match = re.search(r"marketplace/item/(\d+)", url_bruta)
    return match.group(1) if match else None


def descartar_modais(page: Page) -> None:
    """
    Fecha popups de login ou convites de navegação que possam cobrir a tela.
    """
    try:
        # Pressiona Escape para dispensar modais simples
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # Procura botões com aria-label de fechar
        botoes_fechar = page.locator('div[aria-label="Fechar"], div[aria-label="Close"], [aria-label="fechar"]')
        if botoes_fechar.count() > 0:
            botoes_fechar.first.click()
            time.sleep(0.5)
    except Exception as e:
        logger.debug(f"Nenhum modal precisou ser fechado ou erro ao fechar: {e}")


def extrair_tempo_publicacao(texto: str) -> str:
    """
    Identifica padrões como 'Há 15 minutos', 'Há 2 horas', 'Acabou de ser anunciado', 'Anunciado há 1 dia'.
    """
    if not texto:
        return ""
    padroes = [
        r"(?:anunciado\s+)?há\s+\d+\s*(?:minutos?|min|horas?|h|dias?|d|semanas?|sem)(?:\s+em\s+[^,\.\n]+)?",
        r"acabou de ser anunciado",
        r"(?:anunciado\s+)?ontem(?:\s+às\s+\d+:\d+)?",
        r"(?:anunciado\s+)?hoje(?:\s+às\s+\d+:\d+)?"
    ]
    for p in padroes:
        m = re.search(p, texto, re.IGNORECASE)
        if m:
            encontrado = m.group(0).strip()
            return encontrado[:1].upper() + encontrado[1:]
    return ""


def extrair_detalhes_facebook(page: Page) -> tuple[str, str]:
    """
    Extrai tanto o texto completo da descrição quanto o horário/tempo de publicação.
    Retorna (descricao, tempo_anuncio).
    """
    try:
        body_text = page.inner_text("body")
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        tempo_anuncio = extrair_tempo_publicacao(body_text)

        idx_inicio = -1
        for i, l in enumerate(lines):
            l_lower = l.lower()
            if l_lower in ["condição", "condicao", "detalhes"]:
                idx_inicio = i + 1
                if idx_inicio < len(lines) and ("usado" in lines[idx_inicio].lower() or "novo" in lines[idx_inicio].lower()):
                    idx_inicio += 1
                break

        if idx_inicio == -1:
            return "", tempo_anuncio

        fim_tags = [
            "informações do vendedor", "informacoes do vendedor", "patrocinado",
            "pesquisas relacionadas", "detalhes do vendedor", "envie uma mensagem",
            "seleções de hoje", "selecoes de hoje"
        ]
        idx_fim = len(lines)
        for i in range(idx_inicio, len(lines)):
            if any(tag in lines[i].lower() for tag in fim_tags):
                idx_fim = i
                break

        desc_lines = lines[idx_inicio:idx_fim]
        limpas = [
            l for l in desc_lines
            if l.lower() not in ["ver mais", "ver menos", "detalhes"]
            and not l.lower().startswith("wpp ")
            and not l.lower().startswith("whatsapp")
        ]
        return "\n".join(limpas), tempo_anuncio
    except Exception as e:
        logger.debug(f"Erro ao extrair detalhes do anúncio: {e}")
        return "", ""


def coletar_anuncios(
    url_busca: Optional[str] = None,
    limite: int = 20,
    headless: bool = True,
    user_data_dir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Inicia o Playwright, acessa o Marketplace regional e extrai até `limite` anúncios.
    A URL de busca é montada dinamicamente com base nas configurações da cidade e raio.
    """
    config = load_config()
    loc = config.get("localizacao", {})
    cidade = loc.get("cidade", "saopaulo")
    categoria = loc.get("categoria", "electronics")
    raio_km = int(loc.get("raio_km", 50))

    target_url = url_busca or gerar_url_marketplace(cidade, categoria, raio_km)
    perfil_dir = user_data_dir or str(CHROME_PROFILE_DIR)

    logger.info(f"Iniciando coleta de anúncios no Marketplace...")
    logger.info(f"URL Alvo: {target_url}")

    anuncios_coletados: List[Dict[str, Any]] = []

    with sync_playwright() as p:
        context: Optional[BrowserContext] = None

        # 1. Tentativa com o perfil do Chrome configurado
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=perfil_dir,
                headless=headless,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox"
                ],
                viewport={"width": 1366, "height": 768}
            )
        except Exception as e:
            logger.warning(
                f"Chrome principal em uso ou bloqueado ({e}). "
                "Alternando para perfil dedicado '.chrome_profile'..."
            )
            # 2. Fallback para perfil dedicado local do robô
            context = p.chromium.launch_persistent_context(
                user_data_dir=".chrome_profile",
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized"
                ],
                viewport={"width": 1366, "height": 768}
            )

        try:
            page: Page = context.new_page()

            # Navegação
            page.goto(target_url, wait_until="domcontentloaded", timeout=40000)
            time.sleep(3)

            # Dispensa modais de login se houver
            descartar_modais(page)

            # Rola a página progressivamente até carregar a quantidade desejada de anúncios
            tentativas_scroll = 0
            while tentativas_scroll < 5:
                page.evaluate("window.scrollBy(0, 1200);")
                time.sleep(1.2)
                descartar_modais(page)
                elementos = page.locator('a[href*="/marketplace/item/"]').all()
                if len(elementos) >= limite:
                    break
                tentativas_scroll += 1

            elementos = page.locator('a[href*="/marketplace/item/"]').all()
            logger.info(f"Detectados {len(elementos)} elementos potenciais de anúncio na página.")

            urls_vistas = set()

            for elem in elementos:
                if len(anuncios_coletados) >= limite:
                    break

                href = elem.get_attribute("href")
                if not href:
                    continue

                url_limpa = normalizar_url_item(href)
                if url_limpa in urls_vistas:
                    continue

                urls_vistas.add(url_limpa)
                item_id = extrair_id_item(url_limpa)

                # Texto interno do card
                texto_completo = elem.inner_text().strip()
                linhas = [l.strip() for l in texto_completo.split("\n") if l.strip()]

                if not linhas:
                    continue

                # Filtra tags conhecidas do Marketplace que não são preços nem títulos
                tags_ignoradas = {"acabou de ser anunciado", "novo", "em alta", "patrocinado", "destaque"}
                linhas_uteis = [l for l in linhas if l.lower() not in tags_ignoradas]

                if not linhas_uteis:
                    continue

                preco_num = 0.0
                titulo = ""
                localizacao = ""

                # Procura a linha que contém o preço e a primeira linha de texto após todos os preços
                idx_ultimo_preco = -1
                for i, linha in enumerate(linhas_uteis):
                    l_lower = linha.lower()
                    if any(kw in l_lower for kw in ["r$", "us$", "grátis", "gratuito", "free"]):
                        if preco_num == 0.0:
                            precos_encontrados = re.findall(r"(?:r\$|us\$)\s*[\d\.,]+|grátis|gratuito|free", l_lower)
                            if precos_encontrados:
                                preco_num = sanitizar_preco(precos_encontrados[0])
                            else:
                                preco_num = sanitizar_preco(linha)
                        idx_ultimo_preco = i
                    elif idx_ultimo_preco != -1:
                        # Encontrou a linha de título logo após os preços
                        break

                # Título é a primeira linha útil após os preços
                if idx_ultimo_preco != -1 and len(linhas_uteis) > idx_ultimo_preco + 1:
                    titulo = linhas_uteis[idx_ultimo_preco + 1]
                    if len(linhas_uteis) > idx_ultimo_preco + 2:
                        localizacao = linhas_uteis[idx_ultimo_preco + 2]
                else:
                    titulo = linhas_uteis[0]

                # Imagem do card
                imagem_url = None
                img = elem.locator("img").first
                if img.count() > 0:
                    imagem_url = img.get_attribute("src")

                tempo_card = extrair_tempo_publicacao(texto_completo)

                anuncio = {
                    "id_externo": item_id,
                    "url": url_limpa,
                    "titulo": titulo,
                    "preco": preco_num,
                    "localizacao": localizacao,
                    "imagem_url": imagem_url,
                    "texto_bruto": texto_completo,
                    "descricao": "",
                    "tempo_anuncio": tempo_card
                }

                anuncios_coletados.append(anuncio)

            # Extrai descrição profunda e tempo de anúncio para anúncios novos
            from src.database import is_anuncio_processado
            for item in anuncios_coletados:
                if not is_anuncio_processado(item["url"]) and item["preco"] > 1.0:
                    try:
                        logger.info(f"Lendo detalhes completos do vendedor para: '{item['titulo']}'...")
                        detail_page = context.new_page()
                        detail_page.goto(item["url"], wait_until="domcontentloaded", timeout=20000)
                        time.sleep(1.5)
                        desc, tempo_det = extrair_detalhes_facebook(detail_page)
                        item["descricao"] = desc
                        if tempo_det:
                            item["tempo_anuncio"] = tempo_det
                        detail_page.close()
                    except Exception as e:
                        logger.debug(f"Não foi possível obter descrição de {item['url']}: {e}")
                        item["descricao"] = ""

        except Exception as err:
            logger.error(f"Erro durante a raspagem do Marketplace: {err}")
        finally:
            if context:
                context.close()

    logger.info(f"Coleta concluída! {len(anuncios_coletados)} anúncios extraídos com sucesso.")
    return anuncios_coletados


def pesquisar_concorrentes_facebook(
    termo_busca: str,
    cidade: str = "fortaleza",
    context: Optional[BrowserContext] = None,
    limite: int = 10,
    preco_referencia: Optional[float] = None,
    headless: bool = True
) -> Dict[str, Any]:
    """
    Pesquisa concorrentes ativos para o mesmo modelo diretamente no Facebook Marketplace da cidade.
    Calcula o preço médio local real, menor preço concorrente e quantidade de anúncios ativos.
    Descarta acessórios de baixo valor e anúncios com preço simbólico.
    """
    import urllib.parse
    cidade_slug = (cidade or "fortaleza").lower().strip().replace(" ", "")
    termo_limpo = (termo_busca or "").strip()
    q_query = urllib.parse.quote_plus(termo_limpo)
    url_busca = f"https://www.facebook.com/marketplace/{cidade_slug}/search?query={q_query}"

    resultado_padrao = {
        "termo_pesquisado": termo_limpo,
        "cidade": cidade,
        "url_busca": url_busca,
        "total_encontrados": 0,
        "preco_medio": 0.0,
        "preco_min": 0.0,
        "preco_max": 0.0,
        "concorrentes": []
    }

    if not termo_limpo or len(termo_limpo) < 2:
        return resultado_padrao

    def extrair_cards_pesquisa(page: Page) -> List[Dict[str, Any]]:
        page.goto(url_busca, wait_until="domcontentloaded", timeout=35000)
        time.sleep(2.5)
        descartar_modais(page)

        page.evaluate("window.scrollBy(0, 800);")
        time.sleep(1.5)
        descartar_modais(page)

        elementos = page.locator('a[href*="/marketplace/item/"]').all()
        concorrentes_encontrados = []
        urls_vistas = set()

        for elem in elementos[:limite * 2]:
            if len(concorrentes_encontrados) >= limite:
                break
            href = elem.get_attribute("href")
            if not href:
                continue
            url_item = normalizar_url_item(href)
            if url_item in urls_vistas:
                continue
            urls_vistas.add(url_item)

            texto = elem.inner_text().strip()
            linhas = [l.strip() for l in texto.split("\n") if l.strip()]
            tags_ignoradas = {"acabou de ser anunciado", "novo", "em alta", "patrocinado", "destaque"}
            linhas_uteis = [l for l in linhas if l.lower() not in tags_ignoradas]
            if not linhas_uteis:
                continue

            preco_num = 0.0
            idx_ultimo_preco = -1
            for i, linha in enumerate(linhas_uteis):
                l_lower = linha.lower()
                if any(kw in l_lower for kw in ["r$", "us$", "grátis", "gratuito", "free"]):
                    if preco_num == 0.0:
                        precos = re.findall(r"(?:r\$|us\$)\s*[\d\.,]+|grátis|gratuito|free", l_lower)
                        if precos:
                            preco_num = sanitizar_preco(precos[0])
                        else:
                            preco_num = sanitizar_preco(linha)
                    idx_ultimo_preco = i
                elif idx_ultimo_preco != -1:
                    break

            if preco_num <= 1.0:
                continue

            # Se temos preço do anúncio original (ex: R$ 1.500),
            # descarta acessórios (ex: capinha de R$ 30) e valores absurdos
            if preco_referencia and preco_referencia > 60:
                if preco_num < (preco_referencia * 0.35) or preco_num > (preco_referencia * 3.5):
                    continue

            titulo_concorrente = ""
            if idx_ultimo_preco != -1 and len(linhas_uteis) > idx_ultimo_preco + 1:
                titulo_concorrente = linhas_uteis[idx_ultimo_preco + 1]
            else:
                titulo_concorrente = linhas_uteis[0]

            concorrentes_encontrados.append({
                "titulo": titulo_concorrente,
                "preco": preco_num,
                "url": url_item
            })

        return concorrentes_encontrados

    try:
        logger.info(f"Pesquisando concorrentes no Facebook Marketplace ({cidade}) para: '{termo_limpo}'...")
        if context is not None:
            page = context.new_page()
            try:
                concorrentes = extrair_cards_pesquisa(page)
            finally:
                page.close()
        else:
            with sync_playwright() as p:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=".chrome_profile",
                    headless=headless,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                    viewport={"width": 1366, "height": 768}
                )
                try:
                    page = ctx.new_page()
                    concorrentes = extrair_cards_pesquisa(page)
                finally:
                    ctx.close()

        if concorrentes:
            precos = [c["preco"] for c in concorrentes]
            preco_medio = sum(precos) / len(precos)
            preco_min = min(precos)
            preco_max = max(precos)
            logger.info(
                f"Concorrentes encontrados ({len(concorrentes)}): "
                f"Média: R$ {preco_medio:,.2f} | Mín: R$ {preco_min:,.2f} | Máx: R$ {preco_max:,.2f}"
            )
            return {
                "termo_pesquisado": termo_limpo,
                "cidade": cidade,
                "url_busca": url_busca,
                "total_encontrados": len(concorrentes),
                "preco_medio": round(preco_medio, 2),
                "preco_min": round(preco_min, 2),
                "preco_max": round(preco_max, 2),
                "concorrentes": concorrentes
            }
        else:
            logger.info(f"Nenhum concorrente direto encontrado no Facebook para '{termo_limpo}'.")
            return resultado_padrao

    except Exception as e:
        logger.warning(f"Erro ao pesquisar concorrentes no Facebook para '{termo_limpo}': {e}")
        return resultado_padrao

