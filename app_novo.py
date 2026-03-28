# Arquivo proxy/alias criado para compatibilidade com o Render.com
# O comando de inicialização no painel do Render ainda aponta para gunicorn app_novo:app,
# então importamos silenciosamente a nossa nova aplicação principal (app.py).

from app import app

if __name__ == '__main__':
    app.run()
