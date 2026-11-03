from duckduckgo_search import DDGS
import json

ddgs = DDGS()
termo = "Smart TV LG 55 usada brasil"

print("--- PESQUISANDO NA WEB ---")
results = list(ddgs.text(f"site:olx.com.br {termo}", max_results=5))
print("OLX RESULTS:")
for r in results:
    print("TÍTULO:", r.get("title"))
    print("URL:", r.get("href"))
    print("SNIPPET:", r.get("body"))
    print("-" * 40)

results_ml = list(ddgs.text(f"site:mercadolivre.com.br/MLB {termo}", max_results=5))
print("\nMERCADO LIVRE RESULTS:")
for r in results_ml:
    print("TÍTULO:", r.get("title"))
    print("URL:", r.get("href"))
    print("SNIPPET:", r.get("body"))
    print("-" * 40)
