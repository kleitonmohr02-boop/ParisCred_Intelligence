# 🚀 Deploy ParisCred Intelligence - Google Cloud Free Tier

## 📋 Índice Rápido
1. Preparação Local
2. Setup Google Cloud
3. Deploy com Cloud Run
4. Monitoramento
5. Troubleshooting

---

## 1️⃣ Preparação Local

### 1.1 Instalar Google Cloud SDK
```bash
# Windows PowerShell
choco install google-cloud-sdk

# ou download manual
curl https://sdk.cloud.google.com | powershell
```

### 1.2 Autenticar
```bash
gcloud auth login
gcloud config set project seu-projeto-gcp
```

### 1.3 Criar arquivo .env.production
```bash
cp .env.example .env.production

# Editar .env.production com suas variáveis
# (muito importante: SECRET_KEY seguro!)
```

### 1.4 Testar Local
```bash
pip install -r requirements.txt
python migration.py
python app_novo.py

# Verificar em http://localhost:5000
```

---

## 2️⃣ Setup Google Cloud

### 2.1 Criar Novo Projeto GCP
```bash
# Se não tem projeto ainda
gcloud projects create pariscred-saas --organization-id=SEU_ORG_ID

# Ativar
gcloud config set project pariscred-saas
```

### 2.2 Ativar APIs Necessárias
```bash
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  cloudkms.googleapis.com \
  secretmanager.googleapis.com
```

### 2.3 Criar Storage Bucket (Backups)
```bash
gsutil mb -b on gs://pariscred-backups-prod
```

### 2.4 Criar Secrets Manager
```bash
# Salvar SECRET_KEY
echo -n "sua_secret_key_super_segura_aqui" | \
  gcloud secrets create flask-secret-key --data-file=-

# Salvar API Key Evolution
echo -n "CONSIGNADO123" | \
  gcloud secrets create evolution-api-key --data-file=-
```

---

## 3️⃣ Deploy com Cloud Run

### 3.1 Build da Imagem Docker
```bash
# Build local primeiro
docker build -t pariscred:latest .

# Tag para Google Cloud
docker tag pariscred:latest gcr.io/pariscred-saas/pariscred:latest

# Push para Container Registry
docker push gcr.io/pariscred-saas/pariscred:latest
```

### 3.2 Deploy no Cloud Run
```bash
gcloud run deploy pariscred-app \
  --image gcr.io/pariscred-saas/pariscred:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600s \
  --set-env-vars "FLASK_ENV=production" \
  --update-secrets \
    "FLASK_SECRET_KEY=flask-secret-key:latest" \
    "EVOLUTION_API_KEY=evolution-api-key:latest"
```

### 3.3 Configurar Banco de Dados (Cloud SQL)
```bash
# Criar instância PostgreSQL (free tier 30GB)
gcloud sql instances create pariscred-db \
  --database-version POSTGRES_15 \
  --tier db-f1-micro \
  --region us-central1

# Criar banco de dados
gcloud sql databases create pariscred_prod \
  --instance pariscred-db

# Criar usuário
gcloud sql users create admin \
  --instance pariscred-db \
  --password

# Obter IP de conexão
gcloud sql instances describe pariscred-db --format="value(ipAddresses[0].ipAddress)"
```

### 3.4 Atualizar .env no Cloud Run
```bash
gcloud run services update pariscred-app \
  --region us-central1 \
  --set-env-vars \
    "DATABASE_URL=postgresql://admin:SENHA@IP_ACIMA/pariscred_prod" \
    "EVOLUTION_API_URL=http://evolution-api:8080"
```

---

## 4️⃣ Monitoramento & Logs

### 4.1 Ver Logs em Tempo Real
```bash
gcloud run logs read pariscred-app --limit 50 --follow --region us-central1
```

### 4.2 Monitorar CPU/Memória
```bash
gcloud monitoring timeseries list \
  --filter 'metric.type=run.googleapis.com/request_count AND resource.service_id=pariscred-app'
```

### 4.3 Testar Endpoint
```bash
# Obter URL do serviço
gcloud run services describe pariscred-app --region us-central1 --format='value(status.url)'

# Testar
curl https://pariscred-app-xxxxxx.run.app/api/health
```

---

## 5️⃣ Troubleshooting

### Problema: "Permission denied"
```bash
# Dar permissões ao Cloud Run
gcloud projects get-iam-policy pariscred-saas

# Adicionar roles
gcloud projects add-iam-policy-binding pariscred-saas \
  --member=serviceAccount:projeto@appspot.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Problema: "Database connection refused"
```bash
# Verificar conexão Cloud SQL
gcloud sql instances describe pariscred-db

# Autorizar Cloud Run IP
gcloud sql instances patch pariscred-db \
  --clear-authorized-networks \
  --authorized-networks 0.0.0.0/0  # ⚠️ Apenas desenvolvimento!
```

### Problema: "Out of memory"
```bash
# Aumentar memória
gcloud run services update pariscred-app \
  --memory 1Gi \
  --region us-central1
```

---

## 6️⃣ Automação com GitHub Actions (Opcional)

Criar arquivo `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: pariscred-saas
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      
      - name: Build and Push Docker
        run: |
          gcloud builds submit --tag gcr.io/pariscred-saas/pariscred:latest
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy pariscred-app \
            --image gcr.io/pariscred-saas/pariscred:latest \
            --region us-central1 \
            --platform managed
```

---

## ✅ Checklist Pós-Deploy

- [ ] Health check retorna 200 (`/api/health`)
- [ ] Login funciona com credenciais padrão
- [ ] CRM carrega clientes
- [ ] Financeiro simula empréstimo
- [ ] Alertas e KPIs aparecem
- [ ] Logs aparecem no Cloud Logging
- [ ] Backup agendado vai pra Storage
- [ ] CPU médio < 50%
- [ ] Memória média < 400Mi

---

## 📊 Custos Mensais Estimados (Free Tier)

| Serviço | Limite Gratuito | Custo Excedente |
|---------|---|---|
| Cloud Run | 180.000 vCPU-segundos | $0.00002 por segundo |
| Cloud SQL | 30GB armazenamento | $0.26/GB acima |
| Cloud Storage | 5GB | $0.020/GB acima |
| **TOTAL** | **~$0** | **Depende uso** |

---

## 🎯 Próximos Passos

1. ✅ Deploy realizado
2. ⏭️ Configurar domínio custom com Cloud Domains
3. ⏭️ Adicionar SSL/TLS automático
4. ⏭️ Configurar backup automático
5. ⏭️ Setup de CI/CD com GitHub Actions
6. ⏭️ Monitoramento com Cloud Monitoring
7. ⏭️ Alertas com Cloud Alerting

---

**Suporte**: Para erros, verifique `gcloud run logs` e ajuste em `.env`

**Última atualização**: 2026-03-19
