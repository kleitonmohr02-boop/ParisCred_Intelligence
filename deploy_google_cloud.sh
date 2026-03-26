#!/bin/bash
# Deploy ParisCred Intelligence para Google Cloud Run
# Execute este script no terminal

echo "========================================"
echo "  DEPLOY PARISCRED - GOOGLE CLOUD"
echo "========================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Erro: Google Cloud SDK não encontrado${NC}"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}[1/7] Verificando autenticação...${NC}"
gcloud auth login

# Perguntar ID do projeto
echo ""
echo "Digite o ID do seu projeto Google Cloud:"
read PROJECT_ID

# Definir projeto
gcloud config set project $PROJECT_ID

echo -e "${GREEN}[2/7] Ativando APIs necessárias...${NC}"
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com

echo -e "${GREEN}[3/7] Criando arquivo de configurações...${NC}"

# Criar arquivo de configuração temporário
cat > .env.deploy << 'EOF'
FLASK_ENV=production
SECRET_KEY=pc_pariscred_2025_google_cloud
DATABASE_PATH=/tmp/pariscred.db
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_API_KEY=CONSIGNADO123
EVOLUTION_INSTANCE_NAME=Paris_01
LOG_LEVEL=INFO
MAX_MSGS_POR_HORA=30
MAX_MSGS_POR_NUMERO=2
MIN_INTERVALO=20
MAX_INTERVALO=45
EOF

echo -e "${GREEN}[4/7] Fazendo build e deploy no Cloud Run...${NC}"
echo "   (Isso pode levar 5-10 minutos na primeira vez)"

# Deploy usando Cloud Build
gcloud run deploy pariscred-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --timeout 600 \
    --memory 1Gi \
    --cpu 1 \
    --set-env-vars FLASK_ENV=production,DATABASE_PATH=/tmp/pariscred.db

# Verificar se deploy foi bem sucedido
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[5/7] Deploy realizado com sucesso!${NC}"
    
    # Obter URL do serviço
    SERVICE_URL=$(gcloud run services describe pariscred-app --platform managed --region us-central1 --format 'value(status.url)')
    
    echo ""
    echo "========================================"
    echo -e "${GREEN}  DEPLOY CONCLUÍDO!${NC}"
    echo "========================================"
    echo ""
    echo "🌐 URL do seu sistema:"
    echo -e "${YELLOW}$SERVICE_URL${NC}"
    echo ""
    echo "📋 Credenciais de acesso:"
    echo "   Email: admin@pariscred.com"
    echo "   Senha: Admin@2025"
    echo ""
    echo "⚠️  ATENÇÃO: Para o WhatsApp funcionar,"
    echo "   você precisa configurar a Evolution API"
    echo "   separadamente (pode ser local ou outro serviço)"
    echo ""
else
    echo -e "${RED}[ERRO] O deploy falhou${NC}"
    echo "Verifique os logs acima para identificar o problema"
fi

echo -e "${GREEN}[6/7] Configurando domínio personalizado (opcional)...${NC}"
echo "Para configurar domínio personalizado:"
echo "  gcloud run domain-mappings create --domain seu-dominio.com"

echo -e "${GREEN}[7/7] Monitoramento...${NC}"
echo "Para ver logs: gcloud logs read --resource-type=cloud_run_revision"

echo ""
echo "Feito! 🚀"