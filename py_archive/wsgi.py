"""
WSGI entry point para produção com Gunicorn
"""
import os
from app import app

if __name__ == "__main__":
    # Em produção, o Gunicorn executará este arquivo
    # Se rodando localmente, usar Flask dev server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False
    )
