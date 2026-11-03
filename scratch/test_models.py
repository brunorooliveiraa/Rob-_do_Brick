import sys
sys.path.insert(0, ".")
import google.generativeai as genai
from src.config import load_config

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

print("Listando modelos disponíveis:")
try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Erro: {e}")
