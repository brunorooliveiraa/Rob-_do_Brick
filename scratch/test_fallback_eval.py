import sys
sys.path.insert(0, ".")
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import json
import google.generativeai as genai
from src.config import load_config
from src.gemini_parser import SYSTEM_INSTRUCTION

config = load_config()
api_key = config.get("inteligencia_artificial", {}).get("gemini_api_key")
genai.configure(api_key=api_key, transport="rest")

MODELOS_DISPONIVEIS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash"
]

prompt = """
Avalie com rigor o seguinte anúncio de classificados:
Título: "Smart tv Philips 60 4k telão"
Preço Pedido: R$ 1800.00
Descrição Completa do Vendedor:
\"\"\"Tv novinha completa com controle\"\"\"

Retorne o JSON no formato:
{
  "eh_tecnologia": true,
  "marca": "Philips",
  "modelo": "Smart TV 60 4K",
  "termo_busca_otimizado": "Smart TV Philips 60 4K",
  "preco_anunciado": 1800.0,
  "preco_mercado_medio": 2600.0,
  "vale_a_pena": true,
  "justificativa": "Boa margem de revenda"
}
"""

sucesso = False
for m_nome in MODELOS_DISPONIVEIS:
    try:
        print(f"Tentando modelo {m_nome}...")
        model = genai.GenerativeModel(
            model_name=m_nome,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config={"temperature": 0.1, "response_mime_type": "application/json"}
        )
        res = model.generate_content(prompt)
        print(f"Sucesso com {m_nome}!")
        print("Resposta:", res.text[:150])
        sucesso = True
        break
    except Exception as e:
        print(f"Modelo {m_nome} falhou: {e}")

assert sucesso, "Nenhum modelo funcionou!"
print("TESTE DE FALLBACK 100% BEM-SUCEDIDO!")
