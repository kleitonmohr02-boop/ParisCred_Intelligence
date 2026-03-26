# ParisCred Intelligence v2.0

**Sistema de Gestão para Crédito Consignado com Automação WhatsApp**

---

## 🌐 Acesse o Sistema

```
http://localhost:5000
```

### Credenciais de Acesso
| Usuário | Email | Senha |
|---------|-------|-------|
| Admin | admin@pariscred.com | Admin@2025 |
| Vendedor | vendedor@pariscred.com | Vendedor@123 |

---

## ✨ O que tem de Novo na v2.0

### ✅ Melhorias Implementadas

1. **Segurança**
   - Secret key fixa no .env (não perde mais sessão)
   - Validação de inputs (não aceita dados inválidos)
   - CORS específico (só permite domínios autorizados)
   - Logging estruturado (tudo logado para debug)

2. **Evolution API**
   - Disparo real de WhatsApp (não é mais simulação)
   - Verificação de status das instâncias
   - Delay configurável entre envios

3. **Módulo Anti-Ban** ⚠️ NOVO
   - Limite de mensagens por hora (30/h)
   - Limite por número (2/dia)
   - Intervalo variável entre envios (20-45s)
   - Mensagens com variantes (evita detecção)
   - Lista negra (clientes que pediram para não contactar)
   - Circuit breaker para instâncias

4. **Importação de Beneficiários** ⚠️ NOVO
   - Importa planilha Excel (.xlsx, .xls)
   - Detecta colunas automaticamente
   - Normaliza telefones (formato brasileiro)
   - Salva no banco de dados

---

## 📱 Funcionalidades Principais

### 1. CRM Completo
- Gestão de clientes e beneficiários
- Histórico de interações
- Status de cada cliente (novo, em negociação, concluído)

### 2. Campanhas de WhatsApp
- Criar campanhas com mensagem + botões
- Importar beneficiários via Excel
- Disparar em massa via Evolution API
- Acompanhar resultados em tempo real

### 3. Dashboard
- Total de beneficiários
- Campanhas disparadas
- Mensagens enviadas
- Estatísticas por banco/orgão

### 4. Módulo Anti-Ban
- Configurações de segurança
- Números bloqueados
- Lista de não contatar
- Pausar instâncias

---

## 🔧 Configuração Técnica

### Variáveis de Ambiente (.env)
```
FLASK_ENV=development
SECRET_KEY=sua_chave_aqui
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=CONSIGNADO123
EVOLUTION_INSTANCE_NAME=Paris_01

# Anti-Ban (recursos para evitar banimento)
MAX_MSGS_POR_HORA=30
MAX_MSGS_POR_NUMERO=2
MIN_INTERVALO=20
MAX_INTERVALO=45
```

### Docker Compose
O sistema já vem com docker-compose.yml configurado:
- App Flask (porta 5000)
- Evolution API (porta 8080)
- PostgreSQL (banco da Evolution)
- Redis (cache)

### Para rodar com Docker:
```bash
docker-compose up -d
```

---

## 📊 APIs Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/health` | GET | Status do sistema |
| `/api/beneficiarios` | GET/POST | Listar/Criar beneficiários |
| `/api/beneficiarios/importar` | POST | Importar Excel |
| `/api/campanhas` | GET/POST | Listar/Criar campanhas |
| `/api/campanhas/{id}/disparar` | POST | Disparar campanha |
| `/api/whatsapp/status` | GET | Status da instância |
| `/api/antiban/status` | GET | Estatísticas anti-ban |
| `/api/antiban/bloquear` | POST | Bloquear número |
| `/api/admin/usuarios` | GET/POST | Gerenciar usuários |

---

## 🚨 Sobre Banimentos

### O módulo Anti-Ban inclui:
- ⏱️ **Limite de 30 msgs/hora** - Evita spam
- ⏳ **Intervalo de 20-45s** entre envios - Parece humano
- 📝 **Mensagens variadas** - Não repete texto idêntico
- 🚫 **Bloqueio automático** de números que reportam
- 🏷️ **Lista de não contatar** - Respeita pedidos de clientes

### Boas Práticas para Evitar Ban:
1. Não enviar mensagens muito longas
2. Não usar muitos emojis (máx 3-4)
3. Não enviar Links encurtados
4. Não enviar Money/Transfer/BRL repetidamente
5. Respeitar a lista de não contatar
6. Não Disparar para números que pediram para parar

---

## 📁 Estrutura do Projeto

```
ParisCred_Intelligence/
├── app_novo.py          # App Flask principal
├── database.py          # ORM SQLite
├── validators.py        # Validação de inputs
├── modulo_importacao.py # Importação Excel
├── modulo_antiban.py   # Sistema anti-ban
├── docker-compose.yml  # Docker (App + Evolution + DB)
├── .env               # Variáveis de ambiente
├── templates/          # Páginas HTML
│   ├── login.html
│   ├── dashboard.html
│   ├── admin.html
│   └── campanhas.html
└── logs/              # Logs do sistema
```

---

## 📞 Próximas Atualizações Planejadas

- [ ] Dashboard com gráficos (Chart.js)
- [ ] Módulo de simulações de crédito
- [ ] Relatórios em PDF
- [ ] Envio de emails automáticos
- [ ] Multiple instâncias WhatsApp
- [ ] IA para resposta automática

---

## 💰 Custo

| Item | Custo |
|------|-------|
| Servidor (Vercel/Render) | Gratuito |
| Evolution API | Grátis (Docker) |
| Banco SQLite | Grátis |
| **Total** | **R$ 0/mês** |

---

## ✅ Status Atual

| Componente | Status |
|------------|--------|
| App Flask | ✅ Funcionando |
| Banco SQLite | ✅ Funcionando |
| Login/Auth | ✅ Funcionando |
| Dashboard | ✅ Funcionando |
| Importação Excel | ✅ Pronto |
| Evolution API | ⚠️ Precisa configurar |
| Anti-Ban | ✅ Pronto |

---

**Versão**: 2.0.0  
**Data**: Março 2025  
**Desenvolvido por**: ParisCred Intelligence  
**Para**: Paris Cred - www.pariscred.com.br