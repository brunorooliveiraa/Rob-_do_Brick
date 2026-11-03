import sys
sys.path.insert(0, ".")
import google.generativeai as genai
from src.config import load_config

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

for m in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-3.8-flash", "gemini-flash-latest"]:
    try:
        model = genai.GenerativeModel(model_name=m)
        res = model.generate_content("Diga OK")
        print(f"Sucesso com {m}!")
    except Exception as e:
        print(f"Falha com {m}: {type(e)} -> {e}")
