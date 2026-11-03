# Especificação do Dashboard Web Local

O **Dashboard Web Local** é a interface gráfica do **Robô do Brick**. Ele foi projetado para transformar uma automação técnica em um produto comercial intuitivo, permitindo que qualquer comprador configure e monitore sua operação de garimpo diretamente pelo navegador em `http://localhost:5000`.

---

## 🎨 Identidade Visual e Experiência do Usuário

* **Estilo:** Dark Mode moderno com toques de Glassmorphism (efeito vidro translúcido).
* **Paleta de Cores:**
  * Fundo principal: `#0f172a` (Slate Dark)
  * Cartões e Superfícies: `#1e293b` com bordas sutis em `#334155`
  * Destaques e Acentos: `#3b82f6` (Azul Royal) e `#10b981` (Verde Esmeralda para lucros/oportunidades)
  * Alertas e Atenção: `#f59e0b` (Âmbar)
* **Tipografia:** Fonte do sistema com fallback para `Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`.
* **Micro-animações:** Transições suaves em hover nos botões, cards informativos e feedback visual imediato ao salvar configurações.

---

## 🧩 Telas e Componentes do Painel

```
+-----------------------------------------------------------------------------------+
|  🤖 ROBÔ DO BRICK                      [● Sistema Ativo]   [💾 Salvar Alterações] |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  📍 LOCALIZAÇÃO E ALCANCE                   ⚡ NOTIFICAÇÕES & IA                  |
|  +------------------------------------+     +-----------------------------------+ |
|  | Cidade: [ saopaulo               ] |     | Telegram Token: [•••••••••••••••] | |
|  | Raio de Busca: (===O==========)    |     | Chat ID:        [ 123456789     ] | |
|  | Raio Selecionado: 45 km            |     | Gemini API Key: [•••••••••••••••] | |
|  +------------------------------------+     | [ 📲 Testar Alerta Telegram ]     | |
|                                             +-----------------------------------+ |
|                                                                                   |
|  🎯 PRODUTOS MONITORADOS (ALVOS DE COMPRA)               [ + Adicionar Produto ]  |
|  +------------------------------------------------------------------------------+ |
|  | Marca     | Modelo              | Preço Teto  | Revenda Est. | Margem   | Ação  | |
|  |-----------|---------------------|-------------|--------------|----------|-------| |
|  | Apple     | iPhone 13           | R$ 2.200,00 | R$ 2.900,00  | +R$ 700  | [🗑️] | |
|  | Xiaomi    | Poco X6 Pro         | R$ 1.400,00 | R$ 1.900,00  | +R$ 500  | [🗑️] | |
|  | Sony      | PlayStation 5       | R$ 2.300,00 | R$ 3.100,00  | +R$ 800  | [🗑️] | |
|  +------------------------------------------------------------------------------+ |
|                                                                                   |
|  📊 ÚLTIMAS OPORTUNIDADES CAPTURADAS                                              |
|  +------------------------------------------------------------------------------+ |
|  | [Foto] iPhone 13 128GB - R$ 1.850 (Lucro est.: R$ 1.050) - [👉 Abrir Anúncio]| |
|  +------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

---

## 🔌 Endpoints da API Local (REST)

O servidor Flask disponibiliza os seguintes endpoints para comunicação com o frontend:

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/` | Retorna a interface gráfica completa do Dashboard (SPA com Vanilla CSS e JS). |
| `GET` | `/api/config` | Retorna o conteúdo atual do arquivo `config.json`. |
| `POST` | `/api/config` | Salva as novas configurações no `config.json` e sincroniza o banco SQLite. |
| `POST` | `/api/test-telegram` | Dispara uma notificação de teste imediata com os dados de token e chat_id informados. |
| `GET` | `/api/oportunidades` | Retorna o histórico das últimas oportunidades salvas no SQLite. |
| `POST` | `/api/executar-varredura` | Dispara manualmente um ciclo de raspagem para teste imediato. |

---

## ⚡ Ciclo de Vida do Dashboard

* **Iniciação:** Acionado ao clicar em `2_Painel_de_Controle.bat`. O script roda `python dashboard.py` e abre automaticamente a URL `http://localhost:5000` no navegador padrão.
* **Consumo de Memória:** Cerca de 35MB enquanto a janela do painel estiver aberta.
* **Encerramento:** Ao fechar a janela do terminal ou pressionar `Ctrl + C`, o servidor é desligado e libera toda a memória RAM.
