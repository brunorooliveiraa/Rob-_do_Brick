# Plano de Implementação (Roadmap)

Este documento estabelece o cronograma passo a passo para a construção, validação e implantação do **Robô do Brick**, dividido em 3 fases estratégicas ao longo de 3 semanas.

---

## 📅 Visão Geral das Fases

```
[Fase 1: Motor de Busca] ──▶ [Fase 2: Persistência & IA] ──▶ [Fase 3: Regras & Alertas]
      (Semana 1)                       (Semana 2)                       (Semana 3)
  • Ambiente & Playwright         • SQLite (Alvos & Cache)         • Cruzamento de Regras
  • Perfil Real do Chrome          • Deduplicação de Links          • Bot do Telegram
  • Raspagem Top 20               • Normalização com Gemini        • Windows Task Scheduler
```

---

## 🚀 Fase 1: O Motor de Busca (Semana 1)

**Objetivo:** Obter a lista crua dos 20 anúncios mais recentes de eletrônicos no Facebook Marketplace sem disparar bloqueios ou captchas.

### 1.1 Configuração do Ambiente
* Inicializar ambiente virtual Python:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
* Instalar dependências essenciais:
  ```bash
  pip install playwright python-telegram-bot google-generativeai python-dotenv
  playwright install chromium
  ```
  *(Nota: `sqlite3` é nativo do Python e não requer instalação externa).*

### 1.2 Configuração da Sessão Autêntica do Chrome
* Identificar o diretório de dados do Chrome no Windows:
  `C:\Users\<SeuUsuario>\AppData\Local\Google\Chrome\User Data`
* Configurar o Playwright com `launch_persistent_context` para herdar:
  * Cookies de autenticação do Facebook.
  * Localização geográfica configurada no navegador.
  * Resolução de tela e headers HTTP autênticos.
* *Atenção de Segurança:* Fechar instâncias ativas do Chrome antes da execução ou criar um subperfil dedicado para evitar conflitos de bloqueio de arquivo (`SingletonLock`).

### 1.3 Construção da Rotina de Raspagem
* Acessar a URL do Marketplace com parâmetros de:
  * Categoria: Eletrônicos / Celulares.
  * Raio de busca: Região de interesse (ex.: 20 km a 50 km).
  * Ordenação: `sortBy=creation_time_descend` (Mais Recentes Primeiro).
* Implementar seletores robustos para capturar os 20 primeiros cards:
  * Título bruto do anúncio.
  * Preço anunciado (com sanitização de strings para valor numérico float).
  * URL da imagem principal do produto.
  * Link direto do anúncio (URL canônica para evitar variações de parâmetros de tracking).

### ✅ Critérios de Aceite da Fase 1
- [ ] O script abre a página do Marketplace sem exibir tela de login nem bloqueios.
- [ ] O script extrai os primeiros 20 anúncios em menos de 25 segundos.
- [ ] Os dados extraídos são exibidos estruturados no terminal ou salvos em um JSON de teste.

---

## 🧠 Fase 2: Persistência e Inteligência (Semana 2)

**Objetivo:** Filtrar anúncios repetidos em milissegundos e normalizar textos desorganizados em especificações limpas via Inteligência Artificial.

### 2.1 Modelagem e Criação do Banco SQLite
* Criar o arquivo de banco de dados `bric_hunter.db`.
* Executar as migrações/criação das tabelas:
  * `tabela_alvos`: Modelos desejados, preço teto de compra e margem mínima esperada.
  * `tabela_processados`: Histórico de URLs já escaneadas com timestamp e status.
* Alimentar a tabela de alvos com dados reais de produtos de alta liquidez (ex.: iPhone 11 a 15, Poco X5/X6 Pro, Galaxy S21/S22/S23, iPads).

### 2.2 Camada de Deduplicação Ultrarrápida
* Antes de gastar tokens na API do Gemini:
  * Comparar os 20 links raspados contra os registros de `tabela_processados`.
  * Se a URL já existir, o anúncio é imediatamente ignorado.
  * Apenas anúncios verdadeiramente inéditos seguem para a etapa de IA (normalmente 2 a 5 por ciclo).

### 2.3 Integração com a API do Google Gemini
* Configurar a chave de API gratuita via variável de ambiente `GEMINI_API_KEY`.
* Implementar prompt especializado com saída estrita em JSON:
  * Extração de: `marca`, `modelo_padronizado`, `capacidade_armazenamento`, `condicao` (novo/usado/com defeito), `tem_avaria` (boolean), `descricao_avaria`.
* Tratamento de falhas de rede e respeitar limites de requisições por minuto (RPM).

### ✅ Critérios de Aceite da Fase 2
- [ ] Anúncios repetidos são descartados sem chamar a API do Gemini.
- [ ] O Gemini classifica com sucesso anúncios informais (ex.: *"vendo poco x6 pro zerado na caixa urgente"* ➔ Modelo: Poco X6 Pro, Condição: Novo, Avaria: Não).
- [ ] Anúncios com defeito (ex.: *"tela trincada"*, *"somente peças"*) são sinalizados com a flag `tem_avaria = true`.

---

## ⚡ Fase 3: Cruzamento de Regras, Notificação e Agendamento (Semana 3)

**Objetivo:** Avaliar margem de oportunidade, enviar notificações ricas no Telegram e automatizar a execução contínua no Windows.

### 3.1 Cruzamento de Regras de Oportunidade
* Comparar o `modelo_padronizado` retornado pelo Gemini com a lista de alvos da `tabela_alvos`.
* Aplicar a regra de corte:
  * **Se** `modelo_encontrado` está ativo na lista de alvos;
  * **E** `preco_anunciado` <= `preco_teto`;
  * **E** `tem_avaria` == False (ou permitido para revenda de peças);
  * **Então**: Marcar como **OPORTUNIDADE DE COMPRA**.

### 3.2 Integração com o Telegram Bot
* Criar o bot via `@BotFather` e coletar o token da API.
* Identificar o `chat_id` do usuário.
* Criar a mensagem de alerta formatada:
  * Foto do produto em destaque.
  * Título padronizado, Preço de Oferta e Preço Teto.
  * Estimativa de lucro bruto (`Preço Teto - Preço Oferta`).
  * Botão inline clicável: `[👉 Abrir Anúncio no Facebook]`.

### 3.3 Agendamento no Windows Task Scheduler
* Criar script de execução silenciosa (`run_bot.vbs` ou usando `pythonw.exe`) para evitar que janelas do prompt de comando apareçam na tela durante o trabalho diário.
* Configurar tarefa no Agendador do Windows:
  * Disparo: A cada 10 minutos.
  * Ação: Iniciar `pythonw.exe main.py`.
  * Regra de concorrência: Não iniciar nova instância caso a anterior ainda esteja em execução.
* Implementar rotação de logs em arquivo local `logs/bric_hunter.log`.

### ✅ Critérios de Aceite da Fase 3
- [ ] Uma oportunidade simulada dispara um alerta formatado no Telegram em menos de 5 segundos.
- [ ] A notificação inclui a foto real do produto e o botão direto para o anúncio.
- [ ] O Agendador do Windows executa o ciclo a cada 10 minutos sem exibir nenhuma janela visível na tela.
