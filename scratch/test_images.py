import sys
sys.path.insert(0, ".")
from src.scraper import coletar_anuncios

anuncios = coletar_anuncios(limite=5, headless=True)
for a in anuncios:
    print("--- ANUNCIO REAL ---")
    print("Titulo:", a["titulo"])
    print("Preco:", a["preco"])
    print("URL:", a["url"])
    print("Foto URL:", a["imagem_url"][:80] if a["imagem_url"] else "SEM FOTO")
