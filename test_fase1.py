"""
Script de teste e validação da Fase 1:
- Testa a inicialização do Playwright
- Acessa o Facebook Marketplace
- Extrai e exibe os primeiros anúncios encontrados
"""
import sys
import logging

# Garante suporte a UTF-8 / emojis no terminal do Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.scraper import coletar_anuncios

# Configura logs no console para acompanhar a execução
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def main():
    import sys
    is_headless = "--visible" not in sys.argv

    print("=" * 60)
    print(f"🚀 INICIANDO TESTE DA FASE 1: MOTOR DE BUSCA (PLAYWRIGHT)")
    print(f"   Modo Headless: {is_headless}")
    print("=" * 60)

    # Executa a coleta dos primeiros 5 anúncios
    anuncios = coletar_anuncios(limite=5, headless=is_headless)

    print("\n" + "=" * 60)
    print(f"📊 RESULTADO DA COLETA: {len(anuncios)} anúncios capturados")
    print("=" * 60)

    for i, item in enumerate(anuncios, 1):
        print(f"\n[{i}] ------------------------------------------")
        print(f"📌 Título: {item['titulo']}")
        print(f"💵 Preço: R$ {item['preco']:,.2f}")
        print(f"🔗 Link: {item['url']}")
        print(f"🖼️ Imagem: {item['imagem_url'] or 'Sem imagem'}")

    if not anuncios:
        print("\n⚠️ Nenhum anúncio capturado. Possíveis motivos:")
        print("  1. O Facebook solicitou login ou verificação.")
        print("  2. O caminho do perfil do Chrome não foi localizado.")
        print("  3. A URL do Marketplace informada requer ajuste de região.")
    else:
        print("\n✅ FASE 1 VALIDADA COM SUCESSO! Raspador operando normalmente.")

if __name__ == "__main__":
    main()
