import sys
sys.path.insert(0, ".")
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import time
import json
import google.generativeai as genai
from src.config import load_config
from src.gemini_parser import SYSTEM_INSTRUCTION

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

prompt = 'Classifique o produto: "PS4 Slim 1TB por R$ 1300". Retorne JSON com: {"eh_tecnologia": true, "marca": "Sony", "modelo": "PS4 Slim 1TB", "termo_busca_otimizado": "PS4 Slim 1TB"}'

for m in ["gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3.1-flash-lite"]:
    t0 = time.time()
    try:
        model = genai.GenerativeModel(
            model_name=m,
            generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
        )
        res = model.generate_content(prompt)
        dt = time.time() - t0
        print(f"Modelo {m} levou {dt:.2f}s: {res.text.strip()[:100]}")
        break
    except Exception as e:
        print(f"Modelo {m} falhou: {e}")
