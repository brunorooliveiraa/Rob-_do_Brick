# 🤖 Robô do Brick - Motor Autônomo de Arbitragem com IA

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Google%20Gemini-AI%20Studio-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini" />
  <img src="https://img.shields.io/badge/Playwright-Scraping-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright" />
  <img src="https://img.shields.io/badge/Telegram-Bot%20API-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot" />
  <img src="https://img.shields.io/badge/Flask-Dashboard-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/SQLite3-Storage-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
</p>

<p align="center">
  <b>Sistema autônomo de inteligência artificial para garimpo, avaliação de mercado em tempo real e alerta instantâneo de oportunidades de compra no Facebook Marketplace.</b>
</p>

---

## 💡 O Conceito: Arbitragem Autônoma (Zero Lista Fixa)

Diferente de scrapers convencionais que dependem de uma lista engessada de palavras-chave, o **Robô do Brick** atua como um **Avaliador de Mercado Profissional 24/7**:

1. **Varredura Contínua:** Monitora todos os anúncios recém-publicados na categoria de eletrônicos/tecnologia na sua região e raio configurados.
2. **Interpretação Semântica com Gemini IA:** Identifica automaticamente a marca, modelo exato, versão, especificações técnicas e detecta avarias ou defeitos ocultos no texto do anúncio (*"peças"*, *"tela trincada"*, *"sem Face ID"*, *"bloqueado"*).
3. **Cotação de Mercado em Tempo Real:** Pesquisa a média de preços praticada no mercado brasileiro (Mercado Livre, OLX, Buscapé).
4. **Links de Comprovação Imediata:** Anexa até 4 links de referência na web para você auditar o valor de revenda com apenas 1 clique.
5. **Cálculo de Margem & Veredito:** Se o produto atingir os critérios de lucratividade mínima (ex: lucro líquido estimado $\ge$ R\$ 250 e mais de 20% de desconto), o robô emite o selo de oportunidade.
6. **Alerta Imediato no Telegram:** Dispara notificação no celular com foto, preço anunciado, margem de lucro, links de mercado e botão direto para negociar com o vendedor antes da concorrência.

---

## ⚡ Principais Funcionalidades

- 🧠 **Inteligência Artificial Multimodal (Gemini Flash):** Análise rápida e econômica de anúncios com detecção refinada de golpes e produtos danificados.
- 🎯 **Pesquisa Dinâmica de Concorrentes:** Gera links diretos de busca no Mercado Livre, OLX e Buscapé para validação instantânea.
- 📊 **Painel de Controle Web (Dashboard Flask):**
  - Feed visual de todas as oportunidades garimpadas.
  - Telemetria de ciclos de varredura (anúncios coletados, descartados, analisados pela IA).
  - Configuração de filtros: margem mínima (R\$), desconto percentual mínimo (%), cidade, raio em km e aceitação de avarias.
  - Botão de teste para disparo de alerta no Telegram.
- 📱 **Acesso Remoto (Cloudflare Tunnel):** Acompanhe o dashboard e configure o robô do celular, em qualquer lugar, mesmo fora do Wi-Fi de casa.
- 🔕 **Execução 100% Silenciosa em Segundo Plano:** Roda invisível com agendador inteligente:
  - **Diurno (05:00 às 00:00):** Varreduras a cada 10 a 15 minutos.
  - **Madrugada (00:00 às 05:00):** Varreduras a cada 2 horas (economia de requisições).
- 🔋 **Utilitários para Notebooks:** Scripts para manter o robô rodando e conexão Wi-Fi ativa mesmo com a tampa do notebook fechada.

---

## 🏗️ Arquitetura do Sistema

```
  ┌───────────────────────┐
  │ Facebook Marketplace  │
  └──────────┬────────────┘
             │  Playwright (Sessão Real Chrome)
             ▼
  ┌───────────────────────┐
  │     scraper.py        │ ◄─── Filtra anúncios já vistos / grátis (SQLite)
  └──────────┬────────────┘
             │  Anúncios Novos
             ▼
  ┌───────────────────────┐
  │   gemini_parser.py    │ ◄─── Google Gemini IA + Pesquisa de Mercado
  └──────────┬────────────┘
             │  Oportunidade Aprovada
             ▼
  ┌───────────────────────┐       ┌───────────────────────┐
  │     database.py       │ ────► │     dashboard.py      │ (Web UI Local / 4G)
  └──────────┬────────────┘       └───────────────────────┘
             │
             ▼
  ┌───────────────────────┐
  │     notifier.py       │ ────► Telegram Bot (Alerta no Celular)
  └───────────────────────┘
```

---

## 📁 Estrutura de Arquivos

```plaintext
Robo_do_Brick/
├── 1_Conectar_Facebook.bat                  # Login inicial guiado no Facebook
├── 2_Painel_de_Controle.bat                 # Abre o Dashboard Web (localhost:5000)
├── 3_Iniciar_Robo.bat                       # Central de execução (background, avulso, status)
├── Compartilhar_Na_Internet.bat             # Gera túnel Cloudflare seguro para acesso externo
├── Configurar_Energia_Notebook.bat          # Configura plano de energia para rodar com tampa fechada
├── Configurar_Inicializacao_Automatica.bat  # Inicia o robô junto com o Windows
├── Corrigir_Wifi_Ao_Fechar_Tampa.bat        # Impede que o Wi-Fi desligue ao baixar a tampa
├── Iniciar_Servico_Segundo_Plano.vbs        # Launcher VBS silencioso (sem janela CMD)
├── Parar_Servico.bat                        # Encerra o processo em segundo plano
├── dashboard.py                             # Servidor Flask com UI responsiva
├── main.py                                  # Pipeline de execução avulsa / CLI
├── servico_garimpo.py                       # Daemon de varredura contínua com agendamento
├── login_helper.py                          # Assistente de conexão do navegador Playwright
├── verificar_status.py                      # Leitor de status do processo, PID e últimos logs
├── compartilhar_internet.py                 # Gerenciador do binário Cloudflare Tunnel
├── config.json.example                      # Modelo seguro do arquivo de configurações
├── .env.example                             # Modelo de variáveis de ambiente
├── requirements.txt                         # Dependências Python
├── src/
│   ├── config.py                            # Carregamento e sincronização de configurações
│   ├── database.py                          # Camada SQLite (tabelas, telemetria, cache)
│   ├── gemini_parser.py                     # Integração Google Gemini + cotação de mercado
│   ├── scraper.py                           # Automação Playwright para extração de dados
│   └── notifier.py                          # Formatador e disparador de alertas no Telegram
├── templates/
│   └── index.html                           # Interface visual completa do Dashboard
└── docs/                                    # Documentação detalhada de cada módulo
```

---

## 🛠️ Pré-requisitos

1. **Sistema Operacional:** Windows 10 ou 11.
2. **Python:** Versão 3.10 ou superior ([python.org](https://www.python.org/downloads/)). Marque a opção *"Add Python to PATH"* durante a instalação.
3. **Navegador:** Google Chrome instalado.
4. **Contas & Chaves Gratuitas:**
   - **Google Gemini API Key:** Obtenha gratuitamente no [Google AI Studio](https://aistudio.google.com/).
   - **Telegram Bot:** Crie um bot no Telegram falando com o [@BotFather](https://t.me/Botfather) e descubra seu ID numérico com o [@userinfobot](https://t.me/userinfobot).

---

## 🚀 Instalação Rápida

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/brunorooliveiraa/Rob-_do_Brick.git
   cd Rob-_do_Brick
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instale os binários de navegador do Playwright:**
   ```bash
   playwright install chromium
   ```

5. **Crie os arquivos de configuração locais:**
   ```bash
   copy config.json.example config.json
   copy .env.example .env
   ```

---

## 🎮 Operação em 3 Passos Simples

### 1️⃣ Passo 1: Conectar o Facebook
Dê um duplo clique em **`1_Conectar_Facebook.bat`**.
- O navegador abrirá na tela inicial do Facebook.
- Realize o login na sua conta normalmente (marque *"Lembrar senha"*).
- Após logar, volte ao terminal e pressione `ENTER`.
- *Sua sessão fica gravada localmente na pasta `.chrome_profile/` e você não precisará logar novamente.*

### 2️⃣ Passo 2: Configurar Preferências
Dê um duplo clique em **`2_Painel_de_Controle.bat`**.
- O navegador abrirá o painel em `http://localhost:5000`.
- Insira sua **Gemini API Key**, **Token do Telegram** e **Chat ID**.
- Clique no botão **"Testar Alerta Telegram"** para validar.
- Defina a sua cidade (ex: `Fortaleza`, `São Paulo`), raio de busca e critérios de lucro mínimo.
- Clique em **💾 Salvar Configurações**.

### 3️⃣ Passo 3: Iniciar o Garimpo
Dê um duplo clique em **`3_Iniciar_Robo.bat`**.
- Escolha a opção **`[1] Iniciar em SEGUNDO PLANO`**.
- O robô passará a rodar 100% invisível na bandeja do sistema, monitorando e disparando alertas no Telegram sempre que encontrar uma boa oportunidade!

---

## 📱 Notificações no Telegram (Exemplo de Alerta)

Quando o robô encontra uma oportunidade que atende aos seus critérios de lucro, você recebe uma notificação formatada:

```plaintext
🔥 OPORTUNIDADE REAL DE COMPRA!

📱 Produto: iPhone 13 128GB Azul Impecável
📍 Cidade: Fortaleza - CE
💵 Preço Pedido: R$ 1.850,00
📊 Média de Mercado: R$ 2.650,00
💰 Lucro Estimado: R$ 800,00 (+30% de margem)

🔍 Links de Pesquisa de Mercado:
• Mercado Livre: [Ver Ofertas]
• OLX: [Ver Ofertas]
• Buscapé: [Ver Ofertas]

💬 [Falar com Vendedor no Facebook]
```

---

## ⚙️ Menus e Utilitários Avançados

O arquivo **`3_Iniciar_Robo.bat`** oferece uma central completa:

- **`[1] Iniciar em SEGUNDO PLANO:`** Inicia o processo em background usando `pythonw.exe`.
- **`[2] Rodar 1 Varredura Agora:`** Executa um ciclo visível no terminal com logs em tempo real para auditoria imediata.
- **`[3] Verificar Status / Logs:`** Exibe se o processo está rodando, o PID do Windows, estatísticas do último ciclo e as últimas 15 linhas do log.
- **`[4] Parar Robô:`** Encerra o processo em segundo plano de forma graciosa.
- **`[5] Compartilhar na Internet:`** Ativa o Cloudflare Tunnel para acessar o painel de qualquer lugar (4G/5G).

---

## 🔒 Segurança e Privacidade de Dados

Este projeto foi construído seguindo boas práticas de isolamento de credenciais:

- **Zero Exposição de Chaves:** Chaves de API, Tokens do Telegram e caminhos de perfil estão configurados no `.gitignore` e nunca devem ser comitados.
- **Isolamento de Sessão:** Cookies de navegação e arquivos de cache ficam restritos à pasta local `.chrome_profile/`.
- **Banco de Dados Local:** O arquivo `bric_hunter.db` reside apenas na máquina hospedeira.

---

## 📄 Licença

Este projeto é desenvolvido para fins educacionais e automação pessoal de arbitragem. Use de acordo com os termos de serviço das plataformas envolvidas.
