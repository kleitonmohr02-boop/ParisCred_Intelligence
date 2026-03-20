# ParisCred Intelligence - Dockerfile
# SaaS de Crédito Consignado

FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta
EXPOSE 5000

# Variáveis de ambiente padrão
ENV FLASK_APP=app_novo.py
ENV EVOLUTION_API_URL=http://evolution:8080
ENV DATABASE_PATH=/app/app.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app_novo:app"]
