# Integração com o Telegram Bot

O **Telegram** foi escolhido como o canal de saída de alertas do **Robô do Brick** por ser 100% gratuito, sem risco de bloqueio de número (ao contrário de disparos automatizados no WhatsApp) e com suporte nativo a cards ricos com imagem e botões de ação rápida.

---

## 🛠️ Passo a Passo para Criação do Bot

### 1. Criar o Bot no BotFather
1. Abra o Telegram no seu celular ou computador.
2. Pesquise pelo contato oficial **`@BotFather`** (possui selo azul de verificação).
3. Envie o comando `/newbot`.
4. Escolha um nome para exibição (ex.: `Garimpeiro do Bric`).
5. Escolha um nome de usuário que termine em `_bot` (ex.: `bric_garimpo_alerta_bot`).
6. O BotFather responderá com o seu **HTTP API Token**. Ele se parece com:  
   `7123456789:AAFlkjhsdf89234jhksdf98234-sdfsdf`
7. Guarde esse token no seu arquivo `.env` como `TELEGRAM_BOT_TOKEN`.

### 2. Descobrir o seu `chat_id` Pessoal
Para que o bot envie as mensagens diretamente para você:
1. Pesquise no Telegram pelo usuário **`@userinfobot`**.
2. Clique em **Iniciar / Start**.
3. O bot responderá com o seu ID numérico (ex.: `123456789`).
4. Inicie uma conversa com o seu próprio bot recém-criado (clique no link fornecido pelo BotFather e aperte **Começar / Start**).
5. Guarde o ID no seu `.env` como `TELEGRAM_CHAT_ID`.

---

## 🎨 Design do Card de Alerta

Quando uma oportunidade de arbitragem for identificada, o bot envia a foto do anúncio acompanhada de uma legenda rica formatada em HTML/Markdown e um botão de ação imediata:

```text
🚨 OPORTUNIDADE DETECTADA NO BRIC!

📱 Produto: Xiaomi Poco X6 Pro (256GB)
🏷️ Preço Anunciado: R$ 1.250,00
🎯 Seu Preço Teto: R$ 1.400,00
💵 Margem Bruta Estimada: R$ 650,00 (Preço Mercado: R$ 1.900,00)

⚡ Status: Vendedor com urgência!
🛡️ Avarias: Nenhuma detectada

[ 🔗 ABRIR ANÚNCIO NO FACEBOOK ]
```

---

## 💻 Módulo Python de Notificação (`notifier.py`)

Para manter a dependência leve e sem necessidade de loops assíncronos pesados, a integração pode ser feita via requisição HTTP direta com a biblioteca `requests` ou com `python-telegram-bot`:

```python
import os
import requests
from typing import Optional

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_oportunidade(
    marca: str,
    modelo: str,
    preco_anunciado: float,
    preco_teto: float,
    preco_mercado: float,
    url_anuncio: str,
    url_imagem: Optional[str] = None,
    urgencia: bool = False,
    avaria: Optional[str] = None
) -> bool:
    """
    Envia uma notificação rica para o Telegram contendo foto, dados e link direto.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERRO] Credenciais do Telegram não configuradas no ambiente.")
        return False

    margem_estimada = preco_mercado - preco_anunciado if preco_mercado > 0 else preco_teto - preco_anunciado
    status_urgencia = "🔥 Venda Urgente!" if urgencia else "Normal"
    status_avaria = f"⚠️ Atenção: {avaria}" if avaria else "✅ Nenhuma avaria identificada"

    caption = (
        f"🚨 <b>OPORTUNIDADE DE GARIMPO!</b>\n\n"
        f"📱 <b>Aparelho:</b> {marca} {modelo}\n"
        f"💵 <b>Preço Pedido:</b> R$ {preco_anunciado:,.2f}\n"
        f"🎯 <b>Seu Teto:</b> R$ {preco_teto:,.2f}\n"
        f"📈 <b>Lucro Estimado:</b> R$ {margem_estimada:,.2f}\n\n"
        f"⚡ <b>Urgência:</b> {status_urgencia}\n"
        f"🛡️ <b>Condição:</b> {status_avaria}\n"
    )

    # Botão inline com link para abrir o anúncio no navegador ou app
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "👉 Abrir Anúncio no Facebook", "url": url_anuncio}
            ]
        ]
    }

    try:
        # Se houver URL de imagem válida, envia foto com legenda
        if url_imagem and url_imagem.startswith("http"):
            endpoint = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "photo": url_imagem,
                "caption": caption,
                "parse_mode": "HTML",
                "reply_markup": reply_markup
            }
        else:
            # Fallback para mensagem de texto simples se não houver foto
            endpoint = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": caption,
                "parse_mode": "HTML",
                "reply_markup": reply_markup
            }

        response = requests.post(endpoint, json=payload, timeout=10)
        return response.status_code == 200

    except Exception as e:
        print(f"[ERRO] Falha ao enviar alerta no Telegram: {e}")
        return False
```
