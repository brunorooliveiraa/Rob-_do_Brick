import sys
import time
sys.path.insert(0, ".")
import google.generativeai as genai
from src.config import load_config

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

for m in ["gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-3.8-flash"]:
    t0 = time.time()
    try:
        model = genai.GenerativeModel(model_name=m)
        res = model.generate_content("Diga OK", generation_config={"temperature": 0.1})
        elapsed = time.time() - t0
        print(f"Modelo {m}: {elapsed:.2f}s -> {res.text.strip()}", flush=True)
    except Exception as e:
        print(f"Modelo {m} falhou: {e}", flush=True)
