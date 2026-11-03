# Integração com a Inteligência Artificial (Google Gemini)

O **Google Gemini** atua como o normalizador semântico do robô. Anúncios do Marketplace e Bric são notoriamente caóticos: títulos abreviados, erros de digitação, omissões propositais e termos informais dificultam o uso de expressões regulares (Regex).

---

## 🎯 Papel do Gemini no Pipeline

1. **Extração de Entidades:** Identifica a marca exata e o modelo oficial a partir de textos informais (ex.: *"poco x6pro zeraado"* ➔ `Xiaomi Poco X6 Pro`).
2. **Detecção de Avarias e Pegadinhas:** Identifica sinais de defeitos (ex.: *"tela trincada"*, *"só peças"*, *"bateria 68%"*, *"não funciona face id"*, *"bloqueado no icloud"*).
3. **Avaliação de Urgência:** Detecta quando o vendedor está com pressa para se desfazer do item (ex.: *"urgente pra sair hoje"*), indicando maior margem para contraproposta.

---

## 💰 Viabilidade do Free Tier (Custo R$ 0,00)

O **Google AI Studio** disponibiliza um plano gratuito (*Free Tier*) para os modelos Gemini (ex.: `gemini-1.5-flash` ou `gemini-2.0-flash`):

| Limite do Free Tier | Consumo Médio do Robô | Status |
| :--- | :--- | :--- |
| **15 RPM** (Requisições por minuto) | 2 a 5 requisições por ciclo de 10 min | ✅ Com folga |
| **1.500 RPD** (Requisições por dia) | ~200 a 450 requisições por dia | ✅ Menos de 30% da cota |
| **1 milhão TPM** (Tokens por minuto) | ~1.500 tokens por ciclo | ✅ Quase imperceptível |

> **Nota:** Como o script só envia para a IA os anúncios **inéditos** (que passaram pelo filtro do SQLite), você nunca gastará cota reprocessando anúncios antigos.

---

## 🧠 Engenharia de Prompt e JSON Schema

Para garantir respostas rápidas e sem falhas de parseamento, o modelo é instruído a responder exclusivamente em formato JSON (`application/json`).

### System Instruction (Instrução do Sistema)

```text
Você é um especialista em avaliação e precificação de eletrônicos usados e seminovos em classificados brasileiros (Facebook Marketplace e OLX).
Sua função é analisar o título e a descrição de um anúncio de venda e extrair entidades de forma padronizada, identificando avarias ocultas ou explícitas.

Regras estritas:
1. Responda SEMPRE em formato JSON estrito, sem blocos de markdown adicionais.
2. Identifique o modelo exato. Se for um clone/réplica, classifique marca como 'Réplica' e tem_avaria como true.
3. Se o anúncio for de anúncio de acessórios (apenas capinha, apenas caixa vazia, apenas película), marque condicao como 'acessorio' e tem_avaria como true.
4. Identifique avarias: tela trincada, Face ID inativo, bloqueio de conta, bateria degradada (< 80%), linhas na tela, sem som, etc.
```

### JSON Schema Esperado

```json
{
  "marca": "Xiaomi",
  "modelo": "Poco X6 Pro",
  "armazenamento": "256GB",
  "condicao": "semi-novo",
  "tem_avaria": false,
  "descricao_avaria": null,
  "urgencia": true,
  "confianca": 0.95
}
```

---

## 💻 Código de Integração Python (`gemini_parser.py`)

Abaixo está o módulo pronto para integração usando a biblioteca oficial `google-generativeai`:

```python
import json
import os
import google.generativeai as genai
from typing import Optional, Dict, Any

# Configuração da chave de API
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

# Configuração do modelo para saída estrita em JSON
generation_config = {
    "temperature": 0.1,  # Temperatura baixa para máxima precisão e repetibilidade
    "response_mime_type": "application/json"
}

SYSTEM_INSTRUCTION = """
Você é um assistente especializado em classificar anúncios de eletrônicos no Brasil.
Receba o título e preço de um anúncio e retorne um objeto JSON com os seguintes campos:
- marca: (string) Nome oficial da marca (ex: Apple, Xiaomi, Samsung, Sony, Motorola).
- modelo: (string) Nome oficial padronizado (ex: iPhone 13, Poco X6 Pro 5G, Galaxy S23).
- armazenamento: (string ou null) Capacidade informada (ex: 128GB, 256GB).
- condicao: (string) 'novo', 'semi-novo', 'usado', 'defeito', 'acessorio'.
- tem_avaria: (boolean) true se tiver qualquer detalhe/trincado/defeito/peças.
- descricao_avaria: (string ou null) Descrição curta do defeito.
- urgencia: (boolean) true se o vendedor demonstra pressa ("urgente", "sair hoje", etc).
- confianca: (float de 0.0 a 1.0) Seu grau de certeza sobre o modelo.
"""

def normalizar_anuncio(titulo_bruto: str, preco_anunciado: float) -> Optional[Dict[str, Any]]:
    """
    Envia o anúncio bruto para o Gemini e retorna os dados normalizados em dicionário.
    """
    if not GENAI_API_KEY:
        print("[ERRO] GEMINI_API_KEY não configurada no ambiente.")
        return None

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config=generation_config
    )

    prompt = f"""
    Título do anúncio: "{titulo_bruto}"
    Preço anunciado: R$ {preco_anunciado:.2f}
    """

    try:
        response = model.generate_content(prompt)
        dados = json.loads(response.text)
        return dados
    except json.JSONDecodeError as err:
        print(f"[ERRO] Falha ao decodificar JSON retornado pelo Gemini: {err}")
        return None
    except Exception as e:
        print(f"[ERRO] Falha na comunicação com a API do Gemini: {e}")
        return None
```

---

## 🛡️ Tratamento de Limites e Fallback

1. **Tratamento de Rate Limit (HTTP 429):**
   * Se a API do Gemini retornar erro temporário de cota por minuto, o script aguarda 3 segundos com *exponential backoff* antes de tentar o próximo item.
2. **Ignorar Anúncios Flagrados como 'Acessórios':**
   * Quando o modelo classifica `condicao == 'acessorio'`, o anúncio é gravado no SQLite com `eh_oportunidade = 0`, evitando falsos alertas para anúncios de capinhas vendidas como se fossem o celular.
