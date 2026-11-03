import sys
sys.path.insert(0, ".")
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import google.generativeai as genai
from src.config import load_config

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

modelos_candidatos = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-flash-lite-latest",
    "gemini-2.5-pro",
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it"
]

for m in modelos_candidatos:
    try:
        model = genai.GenerativeModel(model_name=m)
        res = model.generate_content("Diga OK em uma palavra.")
        print(f"✅ SUCESSO: {m} está DISPONÍVEL! Resposta: {res.text.strip()}")
    except Exception as e:
        err = str(e)
        if "429" in err:
            print(f"❌ 429 COTA: {m}")
        elif "404" in err:
            print(f"❌ 404 INDISPONÍVEL: {m}")
        else:
            print(f"❌ ERRO {m}: {err[:100]}")
