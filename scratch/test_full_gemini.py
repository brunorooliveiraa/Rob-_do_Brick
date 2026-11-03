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

model = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={
        "temperature": 0.1,
        "response_mime_type": "application/json"
    }
)

prompt = """
Avalie com rigor o seguinte anúncio de classificados:
Título: "Smart tv Philips 60 4k telão"
Preço Pedido: R$ 1800.00
Descrição Completa do Vendedor:
\"\"\"Tv novinha completa com controle original e nf\"\"\"

Retorne o JSON no seguinte formato exato:
{
  "eh_tecnologia": true/false,
  "marca": "Nome da Marca",
  "modelo": "Nome Oficial do Modelo",
  "termo_busca_otimizado": "Nome limpo sem ruído para pesquisar concorrentes",
  "especificacoes": "detalhes de memória, capacidade, processador, etc",
  "condicao": "novo/semi-novo/usado/com defeito",
  "tem_avaria": true/false,
  "descricao_avaria": null ou "detalhes de defeito ou se NÃO for smart",
  "preco_anunciado": 1800.0,
  "preco_mercado_medio": 0.0,
  "margem_estimada_reais": 0.0,
  "margem_percentual": 0.0,
  "vale_a_pena": true/false,
  "justificativa": "explicação curta do porquê vale a pena ou não considerando o estado real"
}
"""

t0 = time.time()
res = model.generate_content(prompt)
dt = time.time() - t0
print(f"Tempo total com gemini-3.5-flash-lite: {dt:.2f}s")
data = json.loads(res.text)
print("Marca:", data.get("marca"))
print("Modelo:", data.get("modelo"))
print("Termo:", data.get("termo_busca_otimizado"))
print("Vale a pena:", data.get("vale_a_pena"))
