import sys
sys.path.insert(0, ".")
import json
import google.generativeai as genai
from src.config import load_config
from src.gemini_parser import SYSTEM_INSTRUCTION

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={
        "temperature": 0.1,
        "response_mime_type": "application/json"
    }
)

prompt = """
Avalie com rigor o seguinte anúncio de classificados:
Título: "JBL Partybox 110"
Preço Pedido: R$ 800.00
Descrição Completa do Vendedor:
\"\"\"Caixa conservada com NF\"\"\"
"""

print("Chamando generate_content...")
res = model.generate_content(prompt)
print("Resposta recebida!")
print(res.text)
