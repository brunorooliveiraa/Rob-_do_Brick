"""
Assistente de Login do Facebook para o Robô do Brick.

Execute este script UMA ÚNICA VEZ para fazer login na sua conta do Facebook.
A sua sessão (cookies e autenticação) ficará salva na pasta local '.chrome_profile'.
Dessa forma, o robô poderá rodar a cada 10 minutos sem conflitar com o seu Chrome de uso diário.
"""
import time
from playwright.sync_api import sync_playwright

def main():
    print("=" * 60)
    print("🔑 ASSISTENTE DE LOGIN - ROBÔ DO BRICK")
    print("=" * 60)
    print("1. O navegador será aberto na página do Facebook.")
    print("2. Faça o login normalmente com sua conta (e marque 'Lembrar senha').")
    print("3. Acesse o Marketplace para confirmar que está funcionando.")
    print("4. Volte a este terminal e pressione ENTER para salvar a sessão.")
    print("=" * 60)

    with sync_playwright() as p:
        # Abre o navegador com o perfil dedicado do bot
        context = p.chromium.launch_persistent_context(
            user_data_dir=".chrome_profile",
            headless=False,
            args=["--start-maximized"],
            viewport=None
        )

        page = context.new_page()
        page.goto("https://www.facebook.com/marketplace", wait_until="domcontentloaded")

        input("\n👉 Quando tiver concluído o login no Facebook, pressione ENTER aqui...")

        print("\n✅ Sessão capturada e salva com sucesso em '.chrome_profile'!")
        context.close()

if __name__ == "__main__":
    main()
