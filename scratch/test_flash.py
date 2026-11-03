import sys
sys.path.insert(0, ".")
import google.generativeai as genai
from src.config import load_config

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

for model_name in ["gemini-3.8-flash", "gemini-flash-latest", "gemini-3.5-flash"]:
    try:
        print(f"Testando {model_name}...")
        m = genai.GenerativeModel(model_name=model_name)
        res = m.generate_content("Diga OK em uma palavra.")
        print(f"Sucesso com {model_name}: {res.text.strip()}")
        break
    except Exception as e:
        print(f"Erro com {model_name}: {e}")
