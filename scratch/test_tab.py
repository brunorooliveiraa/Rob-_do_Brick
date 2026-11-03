from playwright.sync_api import sync_playwright
import time
import re

def extrair_descricao_facebook(page):
    try:
        lines = [l.strip() for l in page.inner_text('body').split('\n') if l.strip()]
        
        # Procura onde começa a descrição (após "Condição" ou "Detalhes")
        idx_inicio = -1
        for i, l in enumerate(lines):
            if l.lower() in ["condição", "condicao", "detalhes"]:
                idx_inicio = i + 1
                # se a próxima linha for "Usado – seminovo" etc, pula ela
                if idx_inicio < len(lines) and ("usado" in lines[idx_inicio].lower() or "novo" in lines[idx_inicio].lower()):
                    idx_inicio += 1
                break
        
        if idx_inicio == -1:
            return ""

        # Procura onde termina (antes de "Informações do vendedor", "Patrocinado", "Pesquisas relacionadas")
        fim_tags = ["informações do vendedor", "informacoes do vendedor", "patrocinado", "pesquisas relacionadas", "detalhes do vendedor", "envie uma mensagem"]
        idx_fim = len(lines)
        for i in range(idx_inicio, len(lines)):
            if any(tag in lines[i].lower() for tag in fim_tags):
                idx_fim = i
                break
                
        desc_lines = lines[idx_inicio:idx_fim]
        # Remove coisas como "Ver mais", "Fortaleza, CE" etc
        limpas = [l for l in desc_lines if l.lower() not in ["ver mais", "ver menos"] and not l.startswith("Wpp ")]
        return "\n".join(limpas)
    except Exception as e:
        return ""

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context('.chrome_profile', headless=True)
    page = ctx.new_page()
    page.goto('https://www.facebook.com/marketplace/item/973879062432616/', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(2000)
    desc = extrair_descricao_facebook(page)
    print("--- DESCRIÇÃO EXTRAÍDA COM SUCESSO ---")
    print(desc)
    ctx.close()
