# Serviço em Segundo Plano e Agendamento Inteligente

O Robô do Brick foi projetado para rodar continuamente em segundo plano, 24 horas por dia, 7 dias por semana, sem interromper o uso diário do seu notebook e com **zero janelas pretas pipocando na tela**.

---

## ⏰ Cronograma Inteligente de Garimpo

O serviço ([`servico_garimpo.py`](file:///c:/Users/Brunin/Desktop/Robo_do_Brick/servico_garimpo.py)) adapta automaticamente o ritmo de varreduras de acordo com o horário:

| Período | Horário | Frequência de Varredura | Motivo |
| :--- | :--- | :--- | :--- |
| **Horário Diurno / Ativo** | **05:00 às 00:00** | **A cada 15 minutos** | Pegar oportunidades na hora em que os anúncios são postados |
| **Madrugada** | **00:00 às 05:00** | **A cada 2 horas** | Economia de requisições e energia durante baixo fluxo de vendas |

---

## 💻 Como Manter o Notebook Rodando 24/7 (Inclusive de Tampa Fechada)

Computadores não executam programas quando estão completamente desligados ou suspensos (*Sleep*). No entanto, você pode fechar a tela do notebook para não gastar energia nem deixar a tela acesa de noite, mantendo o robô 100% ativo na tomada.

### Opção 1: Automática (1 Clique)
Execute o arquivo:
- [`Configurar_Energia_Notebook.bat`](file:///c:/Users/Brunin/Desktop/Robo_do_Brick/Configurar_Energia_Notebook.bat)
Escolha a opção `[1]` para aplicar:
* Suspender por inatividade na tomada: **Nunca**
* Ação ao fechar a tampa na tomada: **Nada a fazer** (*Do nothing*)

### Opção 2: Manual pelo Windows
1. Pressione `Win + R`, digite `control` e abra o **Painel de Controle**.
2. Vá em **Hardware e Sons** > **Opções de Energia**.
3. Na barra lateral esquerda, clique em **Escolher a função do fechamento da tampa**.
4. Na coluna **"Conectado à tomada"**, selecione **"Nada a fazer"**.
5. Clique em **Salvar alterações**.

---

## 🚀 Como Iniciar, Controlar e Parar o Robô

Na pasta do projeto, você tem atalhos dedicados:

1. **[`3_Iniciar_Robo.bat`](file:///c:/Users/Brunin/Desktop/Robo_do_Brick/3_Iniciar_Robo.bat)**: Central interativa:
   - `[1]` Iniciar em Segundo Plano (100% invisível via VBScript/pythonw).
   - `[2]` Rodar 1 Varredura Agora (visível no terminal para testar).
   - `[3]` Verificar Status e últimas linhas de Log.
   - `[4]` Parar o robô.
2. **[`Iniciar_Servico_Segundo_Plano.vbs`](file:///c:/Users/Brunin/Desktop/Robo_do_Brick/Iniciar_Servico_Segundo_Plano.vbs)**: Inicia o robô diretamente sem abrir nenhuma janela preta.
3. **[`Parar_Servico.bat`](file:///c:/Users/Brunin/Desktop/Robo_do_Brick/Parar_Servico.bat)**: Localiza o processo pelo arquivo de trava (`logs/servico_garimpo.lock`) e encerra o serviço com segurança.
4. **[`Configurar_Inicializacao_Automatica.bat`](file:///c:/Users/Brunin/Desktop/Robo_do_Brick/Configurar_Inicializacao_Automatica.bat)**: Adiciona o robô na pasta Inicializar do Windows (`shell:startup`) para ele ligar sozinho sempre que o notebook for ligado ou reiniciado.

