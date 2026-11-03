import re
import json
import logging
import urllib.parse
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from src.config import load_config

logger = logging.getLogger(__name__)


def limpar_termo_busca(marca: str, modelo: str, titulo: str) -> str:
    """
    Extrai um termo de busca limpo e cirúrgico para pesquisas no Facebook Marketplace e OLX.
    Remove ruídos como 'vendo', 'troco', 'urgente', mantendo marca e modelo exatos.
    """
    marca_limpa = (marca or "").strip()
    modelo_limpo = (modelo or "").strip()

    # Se o modelo já contém a marca, não duplica
    if modelo_limpo and marca_limpa and marca_limpa.lower() in modelo_limpo.lower():
        termo = modelo_limpo
    elif marca_limpa and modelo_limpo and marca_limpa.lower() not in ["desconhecida", "não identificada", "genérica"]:
        marca_pura = marca_limpa.split("/")[0].split("(")[0].strip()
        if marca_pura.lower() in modelo_limpo.lower():
            termo = modelo_limpo
        else:
            termo = f"{marca_pura} {modelo_limpo}"
    else:
        termo = modelo_limpo or titulo or ""

    # Remove parênteses com observações
    termo = re.sub(r"\(.*?\)", "", termo)

    # Remove termos de classificados que atrapalham as buscas
    termos_ignorar = [
        "vendo", "troco", "urgente", "seminovo", "semi novo", "semi-novo", "usado",
        "no preço", "preço negociável", "lacrado", "original", "com garantia", "na caixa",
        "nota fiscal", "nf", "leia a descrição", "ótimo estado", "top", "perfeito estado",
        "não troco", "nao troco", "apenas venda", "genérico", "genérica"
    ]
    for palavra in termos_ignorar:
        padrao = re.compile(rf"\b{re.escape(palavra)}\b", re.IGNORECASE)
        termo = padrao.sub("", termo)

    # Limpeza de caracteres especiais
    termo = re.sub(r"[^\w\s\-\+]", " ", termo)
    termo = " ".join(termo.split())
    if not termo:
        termo = titulo.strip()

    return termo


def gerar_links_referencia(marca: str, modelo: str, titulo: str, cidade: str = "fortaleza") -> List[str]:
    """
    Gera única e exclusivamente os dois canais prioritários solicitados:
    1. Pesquisa de Concorrentes no Facebook Marketplace local ({cidade})
    2. Pesquisa de Concorrentes na OLX Ceará (Fortaleza e região)
    """
    termo = limpar_termo_busca(marca, modelo, titulo)
    q_query = urllib.parse.quote_plus(termo)

    return [
        f"https://www.facebook.com/marketplace/{cidade}/search?query={q_query}",
        f"https://www.olx.com.br/estado-ce/fortaleza-e-regiao?q={q_query}"
    ]


SYSTEM_INSTRUCTION = """
Você é um especialista sênior em avaliação, precificação e arbitragem de produtos de tecnologia e eletrônicos no Brasil (Facebook Marketplace e OLX Ceará).

Sua missão é analisar qualquer produto de tecnologia anunciado e determinar autonomamente se o preço pedido é uma OPORTUNIDADE REAL DE MERCADO para compra e revenda lucrativa.

Regras estritas:
1. Responda SEMPRE em formato JSON estrito.
2. Identifique marca, modelo oficial e especificações. Use a DESCRIÇÃO COMPLETA do vendedor como fonte prioritária da verdade.
3. Gere um "termo_busca_otimizado" (nome cirúrgico do produto, ex: 'JBL PartyBox Encore', 'iPhone 11 64GB', 'Acer Nitro 5') sem termos como 'vendo', 'urgente' ou adjetivos.
4. Se for apenas acessório de baixo valor (capinhas, películas, caixa vazia, suporte plástico), marque "eh_tecnologia": false e "vale_a_pena": false.
5. Detecte avarias ou contradições: preste extrema atenção se a descrição desmentir o título (ex: tela trincada, não é smart, apenas peças). Marque "tem_avaria": true e descreva em "descricao_avaria".
6. Estime o preço médio de mercado atual para o produto equivalente no mercado de desapego/usados (referência Facebook Marketplace e OLX).
7. Calcule a margem estimada em R$ (preco_mercado_medio - preco_anunciado) e a margem percentual.
8. Decisão 'vale_a_pena': true se o desconto for expressivo e o produto estiver em boas condições de revenda rápida.
"""


def avaliar_oportunidade_mercado(
    titulo_bruto: str,
    preco_anunciado: float,
    descricao_anuncio: str = "",
    cidade: str = "fortaleza"
) -> Optional[Dict[str, Any]]:
    """
    Avalia qualquer anúncio tecnológico de forma autônoma:
    - Analisa título e descrição completa do vendedor
    - Identifica modelo exato e termo cirúrgico de busca
    - Retorna links exclusivos do Facebook Marketplace e da OLX Ceará
    """
    config = load_config()
    api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")

    if not api_key:
        logger.warning("Chave do Gemini não configurada.")
        return None

    MODELOS_DISPONIVEIS = [
        "gemini-3.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.1-flash-lite"
    ]

    try:
        genai.configure(api_key=api_key, transport="rest")

        desc_formatada = descricao_anuncio.strip() if descricao_anuncio else "Nenhuma descrição fornecida pelo vendedor."

        prompt = f"""
        Avalie com rigor o seguinte anúncio de classificados:
        Título: "{titulo_bruto}"
        Preço Pedido: R$ {preco_anunciado:.2f}

        Descrição Completa do Vendedor:
        \"\"\"{desc_formatada}\"\"\"

        Retorne o JSON no seguinte formato exato:
        {{
          "eh_tecnologia": true/false,
          "marca": "Nome da Marca",
          "modelo": "Nome Oficial do Modelo",
          "termo_busca_otimizado": "Nome limpo sem ruído para pesquisar concorrentes",
          "especificacoes": "detalhes de memória, capacidade, processador, etc",
          "condicao": "novo/semi-novo/usado/com defeito",
          "tem_avaria": true/false,
          "descricao_avaria": null ou "detalhes de defeito ou se NÃO for smart",
          "preco_anunciado": {preco_anunciado},
          "preco_mercado_medio": 0.0,
          "margem_estimada_reais": 0.0,
          "margem_percentual": 0.0,
          "vale_a_pena": true/false,
          "justificativa": "explicação curta do porquê vale a pena ou não considerando o estado real"
        }}
        """

        for nome_modelo in MODELOS_DISPONIVEIS:
            for tentativa in range(2):
                try:
                    model = genai.GenerativeModel(
                        model_name=nome_modelo,
                        system_instruction=SYSTEM_INSTRUCTION,
                        generation_config={
                            "temperature": 0.1,
                            "response_mime_type": "application/json"
                        }
                    )
                    response = model.generate_content(prompt)
                    dados = json.loads(response.text)

                    termo = dados.get("termo_busca_otimizado") or limpar_termo_busca(
                        marca=dados.get("marca") or "",
                        modelo=dados.get("modelo") or "",
                        titulo=titulo_bruto
                    )
                    dados["termo_busca_otimizado"] = termo

                    # Gera exclusivamente Facebook Marketplace e OLX Ceará
                    dados["links_referencia"] = gerar_links_referencia(
                        marca=dados.get("marca") or "",
                        modelo=termo,
                        titulo=titulo_bruto,
                        cidade=cidade
                    )
                    return dados

                except Exception as call_err:
                    err_str = str(call_err).lower()
                    if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                        logger.warning(
                            f"Cota do modelo '{nome_modelo}' temporariamente excedida. "
                            "Alternando para o próximo modelo de backup..."
                        )
                        break  # Sai do retry interno e tenta o próximo modelo da lista
                    elif "404" in err_str:
                        logger.warning(f"Modelo '{nome_modelo}' não disponível nesta versão de API. Alternando...")
                        break
                    else:
                        logger.error(f"Erro na avaliação com {nome_modelo}: {call_err}")
                        if tentativa < 1:
                            import time
                            time.sleep(2)
                        else:
                            break

        return None

    except json.JSONDecodeError as err:
        logger.error(f"Erro ao converter JSON da IA: {err}")
        return None
    except Exception as e:
        logger.error(f"Erro na avaliação com Gemini: {e}")
        return None
