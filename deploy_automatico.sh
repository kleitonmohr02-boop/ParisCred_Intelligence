#!/bin/bash
# ============================================================
# DEPLOY AUTOMÁTICO - ParisCred Intelligence no Google Cloud
# ============================================================
# 
# Este script faz TUDO automaticamente!
# Você só precisa executar ele!
#
# ============================================================

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       DEPLOY PARISCRED INTELLIGENCE v2.0                    ║"
echo "║       Google Cloud Run - Automático                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Cores
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
VERMELHO='\033[0;31m'
AZUL='\033[0;34m'
SEMCOR='\033[0m'

echo -e "${AZUL}[1/8] Verificando Google Cloud SDK...${SEMCOR}"

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${VERMELHO}✗ Google Cloud SDK não está instalado!${SEMCOR}"
    echo ""
    echo "Para instalar, escolha uma opção:"
    echo ""
    echo "A) Windows (PowerShell como Administrador):"
    echo "   choco install google-cloud-sdk"
    echo ""
    echo "B) MacOS:"
    echo "   brew install google-cloud-sdk"
    echo ""
    echo "C) Linux:"
    echo "   curl https://sdk.cloud.google.com | bash"
    echo ""
    echo "Após instalar, execute este script novamente!"
    exit 1
fi

echo -e "${VERDE}✓ Google Cloud SDK encontrado${SEMCOR}"

echo ""
echo -e "${AZUL}[2/8] Autenticando no Google Cloud...${SEMCOR}"
gcloud auth login --brief

echo ""
echo -e "${AMARELO}Para continuar, você precisa de um projeto Google Cloud.${SEMCOR}"
echo "Se não tiver, vá até: https://console.cloud.google.com/projectcreate"
echo ""
echo "Digite o ID do seu projeto (ex: pariscred-app-123456):"
read PROJECT_ID

# Validar projeto
echo ""
echo -e "${AZUL}[3/8] Validando projeto...${SEMCOR}"
gcloud config set project $PROJECT_ID

# Verificar se o projeto existe
if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    echo -e "${VERMELHO}✗ Projeto não encontrado!${SEMCOR}"
    echo "Crie um projeto em: https://console.cloud.google.com/projectcreate"
    exit 1
fi

echo -e "${VERDE}✓ Projeto encontrado: $PROJECT_ID${SEMCOR}"

echo ""
echo -e "${AZUL}[4/8] Ativando APIs necessárias...${SEMCOR}"
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet  
gcloud services enable cloudbuild.googleapis.com --quiet
echo -e "${VERDE}✓ APIs ativadas${SEMCOR}"

echo ""
echo -e "${AZUL}[5/8] Preparando configurações...${SEMCOR}"

# Criar arquivo .env para produção
cat > .env.prod << 'EOF'
FLASK_ENV=production
SECRET_KEY=pc_pariscred_2025_production_google
DATABASE_PATH=/tmp/pariscred.db
EVOLUTION_API_URL=https://api.seu-dominio.com
EVOLUTION_API_KEY=CONSIGNADO123
EVOLUTION_INSTANCE_NAME=Paris_01
LOG_LEVEL=INFO
EOF

echo -e "${VERDE}✓ Configurações criadas${SEMCOR}"

echo ""
echo -e "${AZUL}[6/8] Fazendo build e deploy no Cloud Run...${SEMCOR}"
echo -e "${AMARELO}   Este processo pode levar 5-15 minutos na primeira vez...${SEMCOR}"
echo ""

# Deploy com Cloud Build
gcloud run deploy pariscred-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 900 \
    --max-instances 1 \
    --min-instances 0 \
    --service-account default \
    --ingress internal-and-cloud-load-balancing \
    --set-env-vars "FLASK_ENV=production,DATABASE_PATH=/tmp/pariscred.db,PYTHONUNBUFFERED=1" \
    --label "app=pariscred,version=v2.0"

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${VERDE}═══════════════════════════════════════════════════════════════${SEMCOR}"
    echo -e "${VERDE}  ✓ DEPLOY CONCLUÍDO COM SUCESSO!${SEMCOR}"
    echo -e "${VERDE}═══════════════════════════════════════════════════════════════${SEMCOR}"
    echo ""
    
    # Obter URL
    SERVICE_URL=$(gcloud run services describe pariscred-app --platform managed --region us-central1 --format 'value(status.url)' 2>/dev/null || echo "ERRO")
    
    echo -e "${AZUL}🌐 SEU SISTEMA ESTÁ ONLINE:${SEMCOR}"
    echo ""
    echo -e "   ${VERDE}$SERVICE_URL${SEMCOR}"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "📋 INFORMAÇÕES DE ACESSO:"
    echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   Email:    admin@pariscred.com"
    echo "   Senha:    Admin@2025"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "⚠️  PRÓXIMOS PASSOS:"
    echo "   1. Acesse o link acima e faça login"
    echo "   2. Para WhatsApp funcionar, configure a Evolution API"
    echo "   3. A variável EVOLUTION_API_URL precisa apontar para sua API"
    echo ""
    
    # Salvar URL em arquivo
    echo "$SERVICE_URL" > DEPLOY_URL.txt
    echo -e "${VERDE}✓ URL salva em DEPLOY_URL.txt${SEMCOR}"
    
else
    echo -e "${VERMELHO}✗ O deploy falhou!${SEMCOR}"
    echo "Verifique os erros acima e tente novamente."
    exit 1
fi

echo ""
echo -e "${AZUL}[7/8] Configurando domínio personalizado (opcional)...${SEMCOR}"
echo "Para adicionar um domínio próprio (ex: sistema.pariscred.com.br):"
echo "   gcloud run domain-mappings create --domain seu-dominio.com"

echo ""
echo -e "${AZUL}[8/8] Verificando status...${SEMCOR}"
echo ""
echo -e "${VERDE}Parabéns! Seu sistema está no ar! 🎉${SEMCOR}"
echo ""
echo "Feito! Conteúdo gerado automaticamente."