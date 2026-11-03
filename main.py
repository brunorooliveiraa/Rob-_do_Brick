import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Suporte a UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import load_config, LOGS_DIR
from src.database import (
    init_db,
    is_anuncio_processado,
    registrar_anuncio
)
from src.scraper import coletar_anuncios, pesquisar_concorrentes_facebook
from src.gemini_parser import avaliar_oportunidade_mercado
from src.notifier import enviar_alerta_oportunidade

# Configura logs em arquivo e console
log_file = LOGS_DIR / "bric_hunter.log"
main_handlers = [logging.FileHandler(log_file, encoding="utf-8")]
if sys.stdout is not None:
    main_handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=main_handlers
)
logger = logging.getLogger(__name__)


def executar_ciclo_garimpo() -> int:
    """
    Executa um ciclo completo de garimpo autônomo com validação local:
    1. Raspa anúncios recentes de tecnologia na região (Facebook Marketplace)
    2. Descarta duplicatas no SQLite
    3. Para cada produto novo, a IA extrai o modelo exato e termo de busca cirúrgico
    4. O robô re-pesquisa o modelo no Facebook Marketplace local para extrair concorrentes ativos
    5. Compara o preço anunciado diretamente com os concorrentes locais e calcula giro rápido
    6. Dispara alerta rico no Telegram com links exclusivos do Facebook e da OLX Ceará
    """
    config = load_config()
    if not config.get("execucao", {}).get("ativo", True):
        logger.info("Robô pausado pelo usuário nas configurações (execucao.ativo = False).")
        return 0

    init_db()

    cidade = config.get("localizacao", {}).get("cidade", "Fortaleza")
    criterios = config.get("criterios_arbitragem", {})
    margem_minima = float(criterios.get("margem_minima_reais", 250.0))
    desconto_minimo = float(criterios.get("desconto_minimo_percentual", 20.0))
    desconto_giro_rapido = float(criterios.get("desconto_giro_rapido_reais", 150.0))
    aceita_avaria = criterios.get("aceita_avaria", False)

    logger.info(f"--- CICLO DE GARIMPO AUTÔNOMO (FACEBOOK + OLX CEARÁ) INICIADO ---")
    logger.info(f"Região: {cidade} | Lucro Mínimo: R$ {margem_minima:,.2f} | Giro Rápido: -R$ {desconto_giro_rapido:,.2f} | Desconto: {desconto_minimo}%")

    anuncios = coletar_anuncios(limite=35, headless=True)
    novas_oportunidades = 0
    repetidos = 0
    ignorados_preco = 0
    analisados_ia = 0

    for item in anuncios:
        url = item["url"]
        titulo = item["titulo"]
        preco = item["preco"]
        imagem_url = item["imagem_url"]
        id_externo = item["id_externo"]
        descricao = item.get("descricao", "")

        # 1. Filtro Ultrarrápido de Cache
        if is_anuncio_processado(url):
            repetidos += 1
            logger.debug(f"Anúncio já avaliado: {titulo}")
            continue

        if preco <= 1.0:
            # Anúncios de R$ 1 ou R$ 0 costumam ser chamarizes sem preço real
            ignorados_preco += 1
            logger.info(f"Anúncio '{titulo}' ignorado por preço simbólico (R$ {preco:.2f}).")
            registrar_anuncio(
                url_anuncio=url,
                titulo_bruto=titulo,
                preco_anunciado=preco,
                url_imagem=imagem_url,
                id_externo=id_externo,
                dados_avaliacao={
                    "marca": "Ignorado",
                    "modelo": titulo,
                    "preco_mercado_medio": 0.0,
                    "margem_estimada_reais": 0.0,
                    "margem_percentual": 0.0,
                    "justificativa": "Anúncio ignorado automaticamente: preço simbólico ou grátis (R$ 0/1).",
                    "links_referencia": [],
                    "eh_tecnologia": False,
                    "vale_a_pena": False
                },
                eh_oportunidade=False,
                notificado=False,
                descricao_anuncio=descricao or "Preço simbólico (R$ 0 ou R$ 1)",
                preco_venda_rapida=0.0,
                desconto_giro_rapido=0.0,
                tempo_anuncio=item.get("tempo_anuncio", "")
            )
            continue

        logger.info(f"Novo anúncio em análise: '{titulo}' por R$ {preco:,.2f}")
        analisados_ia += 1

        # 2. Avaliação Preliminar com Gemini (Identificação do Modelo Exato e Termo Cirúrgico)
        dados_ia = avaliar_oportunidade_mercado(titulo, preco, descricao, cidade=cidade)
        time.sleep(4.0)  # cadência de 4s para respeitar rigorosamente o teto gratuito de 15 requisições/minuto

        eh_oportunidade = False
        notificado = False
        preco_venda_rapida = 0.0
        dados_concorrentes = None

        if dados_ia:
            eh_tecnologia = dados_ia.get("eh_tecnologia", False)
            marca = dados_ia.get("marca") or "Não identificada"
            modelo = dados_ia.get("modelo") or titulo
            termo_busca = dados_ia.get("termo_busca_otimizado") or modelo
            specs = dados_ia.get("especificacoes")
            tem_avaria = dados_ia.get("tem_avaria", False)
            descricao_avaria = dados_ia.get("descricao_avaria")
            vale_a_pena_ia = dados_ia.get("vale_a_pena", False)
            justificativa = dados_ia.get("justificativa") or ""
            links_ref = dados_ia.get("links_referencia") or []

            # 3. Re-pesquisa Ativa de Concorrentes no Facebook Marketplace da Região
            if eh_tecnologia:
                logger.info(f"Pesquisando concorrentes locais no Facebook para '{termo_busca}'...")
                dados_concorrentes = pesquisar_concorrentes_facebook(
                    termo_busca=termo_busca,
                    cidade=cidade,
                    preco_referencia=preco,
                    headless=True
                )

                if dados_concorrentes and dados_concorrentes.get("total_encontrados", 0) > 0:
                    preco_mercado = float(dados_concorrentes["preco_medio"])
                    dados_ia["preco_mercado_medio"] = preco_mercado
                    dados_ia["total_concorrentes_facebook"] = dados_concorrentes["total_encontrados"]
                    dados_ia["preco_min_facebook"] = dados_concorrentes["preco_min"]
                    dados_ia["preco_max_facebook"] = dados_concorrentes["preco_max"]
                    logger.info(
                        f"Média real do Facebook ({cidade}): R$ {preco_mercado:,.2f} "
                        f"baseada em {dados_concorrentes['total_encontrados']} anúncios ativos."
                    )
                else:
                    preco_mercado = float(dados_ia.get("preco_mercado_medio") or 0.0)
                    dados_ia["total_concorrentes_facebook"] = 0
                    dados_ia["preco_min_facebook"] = 0.0
                    dados_ia["preco_max_facebook"] = 0.0
            else:
                preco_mercado = 0.0

            # 4. Fórmula Profissional de Giro Rápido
            if preco_mercado > 0:
                preco_venda_rapida = max(preco, preco_mercado - desconto_giro_rapido)
                margem_reais = preco_venda_rapida - preco
                margem_pct = (margem_reais / preco_venda_rapida * 100) if preco_venda_rapida > 0 else 0.0
            else:
                margem_reais = 0.0
                margem_pct = 0.0

            dados_ia["margem_estimada_reais"] = margem_reais
            dados_ia["margem_percentual"] = margem_pct

            logger.info(
                f"Análise Final: {marca} {modelo} | Preço Vendedor: R$ {preco:,.2f} | "
                f"Mercado Local: R$ {preco_mercado:,.2f} | Venda Rápida: R$ {preco_venda_rapida:,.2f} | "
                f"Lucro no Bolso: +R$ {margem_reais:,.2f} ({margem_pct:.0f}%)"
            )

            # 5. Regra de Arbitragem com Lucro Real Comprovado
            condicao_avaria = (not tem_avaria) or aceita_avaria

            if (
                eh_tecnologia and
                condicao_avaria and
                vale_a_pena_ia and
                margem_reais >= margem_minima and
                margem_pct >= desconto_minimo
            ):
                logger.info(f"🔥 OPORTUNIDADE REAL DE ARBITRAGEM: {marca} {modelo} com lucro líquido de R$ {margem_reais:,.2f}!")
                eh_oportunidade = True
                novas_oportunidades += 1

                # 6. Disparo de Notificação Rica no Telegram
                notificado = enviar_alerta_oportunidade(
                    marca=marca,
                    modelo=modelo,
                    especificacoes=specs,
                    preco_anunciado=preco,
                    preco_mercado_medio=preco_mercado,
                    margem_estimada_reais=margem_reais,
                    margem_percentual=margem_pct,
                    justificativa=justificativa,
                    links_referencia=links_ref,
                    url_anuncio=url,
                    url_imagem=imagem_url,
                    avaria=descricao_avaria,
                    preco_venda_rapida=preco_venda_rapida,
                    desconto_giro_rapido=desconto_giro_rapido,
                    descricao_vendedor=descricao,
                    dados_concorrentes=dados_concorrentes,
                    cidade=cidade
                )

        # 7. Registra parecer completo no SQLite
        if dados_ia is not None:
            registrar_anuncio(
                url_anuncio=url,
                titulo_bruto=titulo,
                preco_anunciado=preco,
                url_imagem=imagem_url,
                id_externo=id_externo,
                dados_avaliacao=dados_ia,
                eh_oportunidade=eh_oportunidade,
                notificado=notificado,
                descricao_anuncio=descricao,
                preco_venda_rapida=preco_venda_rapida,
                desconto_giro_rapido=desconto_giro_rapido,
                tempo_anuncio=item.get("tempo_anuncio", "")
            )

    from src.database import salvar_telemetria_ciclo
    now = datetime.now()
    telemetria = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp_formatado": now.strftime("%d/%m/%Y às %H:%M:%S"),
        "hora_formatada": now.strftime("%H:%M:%S"),
        "total_coletados": len(anuncios),
        "repetidos": repetidos,
        "ignorados_preco": ignorados_preco,
        "novos_analisados": analisados_ia,
        "novas_oportunidades": novas_oportunidades
    }
    salvar_telemetria_ciclo(telemetria)

    logger.info(
        f"--- FIM DO CICLO: {novas_oportunidades} nova(s) oportunidade(s) autônoma(s) detectada(s). "
        f"Coletados: {len(anuncios)} | Já avaliados: {repetidos} | Ignorados (R$ 0): {ignorados_preco} | "
        f"Novos analisados pela IA: {analisados_ia} ---"
    )
    return telemetria


if __name__ == "__main__":
    executar_ciclo_garimpo()
