# Robô do Brick - Motor de Arbitragem Autônoma de Tecnologia

Sistema de Inteligência Artificial para garimpo, avaliação de mercado em tempo real e alerta instantâneo de oportunidades de compra no Facebook Marketplace / Bric e OLX.

---

## 🚀 O Novo Paradigma: Arbitragem Autônoma (Zero Lista Fixa)

Diferente de bots tradicionais que dependem de uma lista manual e engessada de produtos, o **Robô do Brick** opera como um **Avaliador Profissional de Mercado Autônomo**:

1. **Varredura Ampla de Tecnologia:** O robô varre **todos os anúncios recentes da categoria de eletrônicos/tecnologia** na cidade e raio configurados (Fortaleza, São Paulo, etc.).
2. **Avaliação Semântica com IA:** O Google Gemini analisa o produto anunciado, identifica marca, modelo oficial, especificações e detecta defeitos/avarias ("tela trincada", "sem face id", "peças").
3. **Pesquisa de Mercado em Tempo Real:** A IA estima o preço médio de mercado atual para aquele produto usado/seminovo no Brasil (com base em referências de plataformas como Mercado Livre, OLX e Buscapé).
4. **4 Links de Comprovação:** O robô localiza e anexa **até 4 links de referência na web** para você comprovar o valor de revenda com 1 clique.
5. **Cálculo de Margem & Veredito:** Se o produto oferecer uma margem líquida atraente (ex: lucro acima de R$ 250 e mais de 20% de desconto), o robô emite o veredito: `🔥 Oportunidade Real de Compra!`
6. **Alerta Instantâneo no Telegram:** Dispara no seu celular a foto do produto, valor pedido, preço médio de mercado, lucro estimado em R$, links de referência e o botão para falar com o vendedor antes de todo mundo!

---

## 🎛️ Operação Comercial em 2 Botões

| Atalho | Finalidade |
| :--- | :--- |
| **🔑 `1_Conectar_Facebook.bat`** | Abre o navegador para login único no Facebook (cookies salvos na pasta `.chrome_profile` com total segurança e privacidade). |
| **🎛️ `2_Painel_de_Controle.bat`** | Abre o Dashboard Web (`localhost:5000`) para ajustar a cidade, raio em km, critérios de lucro mínimo e ver o feed de oportunidades. |
| **🚀 `3_Iniciar_Robo.bat`** | Executa a varredura autônoma no modo silencioso de segundo plano. |
