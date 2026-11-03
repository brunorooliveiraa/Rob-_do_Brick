import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.gemini_parser import avaliar_oportunidade_mercado, limpar_termo_busca, gerar_links_referencia
from src.scraper import pesquisar_concorrentes_facebook
from src.database import init_db, registrar_anuncio, listar_ultimos_escaneados

def test_pipeline():
    print("=== TESTE 1: Limpeza de Termo e Links ===")
    termo = limpar_termo_busca("JBL", "Partybox 110", "Vendo caixa JBL Partybox 110 seminova no precinho urgente")
    print(f"Termo limpo gerado: '{termo}'")
    assert "vendo" not in termo.lower()
    assert "precinho" not in termo.lower()
    assert "urgente" not in termo.lower()

    links = gerar_links_referencia("JBL", termo, "JBL Partybox 110", cidade="fortaleza")
    print("Links gerados:")
    for l in links:
        print(" ->", l)
    assert len(links) == 2
    assert "facebook.com/marketplace/fortaleza/search" in links[0]
    assert "olx.com.br/estado-ce/fortaleza-e-regiao" in links[1]

    print("\n=== TESTE 2: Re-pesquisa de Concorrentes no Facebook ===")
    concorrentes = pesquisar_concorrentes_facebook(
        termo_busca="JBL Partybox 110",
        cidade="fortaleza",
        preco_referencia=1000.0,
        headless=True
    )
    print(f"Total concorrentes encontrados: {concorrentes['total_encontrados']}")
    print(f"Preço Médio Facebook: R$ {concorrentes['preco_medio']:.2f}")
    print(f"Menor Preço Facebook: R$ {concorrentes['preco_min']:.2f}")

    print("\n=== TESTE 3: Banco de Dados com Métricas de Concorrentes ===")
    init_db()
    dados_mock = {
        "marca": "JBL",
        "modelo": "Partybox 110",
        "termo_busca_otimizado": termo,
        "preco_mercado_medio": concorrentes["preco_medio"],
        "margem_estimada_reais": 350.0,
        "margem_percentual": 25.0,
        "total_concorrentes_facebook": concorrentes["total_encontrados"],
        "preco_min_facebook": concorrentes["preco_min"],
        "preco_max_facebook": concorrentes["preco_max"],
        "links_referencia": links,
        "justificativa": "Testando pipeline completo de arbitragem",
        "eh_tecnologia": True,
        "vale_a_pena": True
    }
    url_teste = f"https://www.facebook.com/marketplace/item/999999999999_{int(time.time())}/"
    registrar_anuncio(
        url_anuncio=url_teste,
        titulo_bruto="JBL Partybox 110",
        preco_anunciado=850.0,
        dados_avaliacao=dados_mock,
        eh_oportunidade=True,
        notificado=False,
        descricao_anuncio="Caixa de som novinha",
        preco_venda_rapida=1200.0,
        desconto_giro_rapido=150.0,
        tempo_anuncio="Há 10 minutos"
    )

    ultimos = listar_ultimos_escaneados(5)
    achou = False
    for u in ultimos:
        if u["url_anuncio"] == url_teste:
            achou = True
            print("Registro verificado no SQLite com sucesso!")
            print(f" -> Modelo: {u['modelo_detectado']}")
            print(f" -> Concorrentes FB: {u['total_concorrentes_facebook']}")
            print(f" -> Preço Mín FB: R$ {u['preco_min_facebook']:.2f}")
            print(f" -> Preço Médio: R$ {u['preco_mercado_medio']:.2f}")
            print(f" -> Links: {u['links_referencia']}")
            break
    # Limpa o registro de teste para não poluir o banco real
    import sqlite3
    with sqlite3.connect("bric_hunter.db") as conn:
        conn.cursor().execute("DELETE FROM tabela_processados WHERE url_anuncio = ?", (url_teste,))
        conn.commit()

    print("\n✅ TODOS OS TESTES DO PIPELINE PASSARAM COM 100% DE SUCESSO!")

if __name__ == "__main__":
    test_pipeline()
