import sys
sys.path.insert(0, ".")
import google.generativeai as genai
from src.config import load_config

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

try:
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash-lite",
        tools=[{"google_search_retrieval": {}}]
    )
    res = model.generate_content("Qual o preço médio de TV LG 55 no Brasil?")
    print("SUCCESS 3.5:", res.text[:300])
except Exception as e:
    print("ERR 3.5:", e)
