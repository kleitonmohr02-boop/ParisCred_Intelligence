# 🚀 PROMPT EXECUTIVO DEFINITIVO
## ParisCred Intelligence - O Sistema de CRM Inteligente mais Avançado do Mercado de Consignado

---

## 🎯 VISÃO DO PROJETO

Criar o **巴黎Cred Intelligence** - um ecossistema de CRM completo, vivo e inteligente que vai revolucionar a forma como a Paris Cred vende consignado. Um sistema que combina gestão de clientes, automação de WhatsApp, inteligência artificial em todas as etapas, análise de extratos, e um "cérebro corporativo" que работает 24/7 para otimizar resultados.

**DIFERENCIAL MUNDIAL**: Este não é apenas mais um CRM. É um assistente inteligente que trabalha junto com vendedores, gestores e admin, aprendendo com os dados e sugerindo melhorias proativas. É a Paris Cred viva dentro do computador.

---

## 📋 ENTREGÁVEIS ESPERADOS

### 1. Frontend Unificado
- Interface web completa (React + Tailwind)
- Dashboard interativo com gráficos em tempo real
- Pipeline Kanban com drag-and-drop
- Chat com Coach IA integrado
- Análise de extratos por upload de PDF
- Área do cliente (portal)
- Totalmente mobile-first

### 2. Backend Robusto
- APIs REST completas (FastAPI)
- Banco de dados SQLite com schema completo
- Autenticação JWT com roles (admin, gestor, vendedor)
- Módulos de IA integrados
- Integração Evolution API para WhatsApp
- Sistema Anti-Ban inteligente
- Logs e monitoramento

### 3. Módulos de IA
- **Coach IA**: Assistente de vendas que ajuda vendedores em tempo real
- **Supervisor IA**: Monitora pipeline, alerta gargalos, sugere melhorias
- **Analisador de Extrato**: Lê PDFs de extratos e identifica oportunidades
- **Qualificador de Leads**: Score automático com sugestões de abordagem
- **Calculadora**: Simulações de portabilidade e refinanciamento

### 4. Infraestrutura
- Docker configurado (App + Evolution + DB)
- Deploy para Google Cloud Run
- Variáveis de ambiente seguras
- Backup automático

---

## 🏗️ ESTRUTURA DO PROJETO

```
pariscred-intelligence/
├── backend/
│   ├── app.py                          # FastAPI main
│   ├── routes/
│   │   ├── auth.py                     # Login, registro
│   │   ├── leads.py                    # CRUD leads
│   │   ├── pipeline.py                 # Movimentação kanban
│   │   ├── coach.py                    # Chat IA
│   │   ├── extrato.py                  # Análise PDF
│   │   ├── whatsapp.py                 # Disparos
│   │   └── dashboard.py                # Métricas
│   ├── models/                         # Models SQL
│   ├── services/                        # Lógica de negócio
│   └── utils/                          # Helpers
├── frontend/
│   ├── src/
│   │   ├── pages/                      # Páginas React
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Pipeline.jsx
│   │   │   ├── LeadDetail.jsx
│   │   │   ├── Coach.jsx
│   │   │   ├── Extrato.jsx
│   │   │   └── Academy.jsx
│   │   ├── components/                # Componentes
│   │   └── api/                        # Cliente API
├── database/
│   └── migrations/                     # SQL
├── docker-compose.yml                  # Tudo
├── Dockerfile                          # App container
└── .env                                # Config
```

---

## 🎨 DESIGN SYSTEM

### Cores
- **Primária**: Azul Paris (#1E3A5F) - Confiança, profissionalismo
- **Secundária**: Verde Success (#10B981) - Dinheiro, oportunidade
- **Acento**: Azul claro (#3B82F6) - Tecnologia, inovação
- **Fundo**: Cinza claro (#F9FAFB)
- **Texto**: Cinza escuro (#1F2937)

### Princípios UI/UX
- Mobile-first (90% usuários mobile)
- Botões de ação sempre visíveis
- WhatsApp flutuante em todas as telas
- Feedback visual instantâneo
- Hierarquia clara de informações
- Ícones universais e grandes
- Forms com validação em tempo real

---

## 🔧 FUNCIONALIDADES DETALHADAS

### A. Autenticação e Permissões
- Login com email/senha (JWT)
- Roles: Admin, Gestor, Vendedor
- Admin vê tudo, Gestor vê equipe, Vendedor vê apenas seus leads
- Recuperação de senha
- Sessão persistente

### B. Pipeline de Vendas (Kanban)
**Etapas do funil:**
1. `lead_novo` → Lead recebido
2. `contato_inicial` → Primeiro contato feito
3. `qualificado` → Dados completos, viabilidade verificada
4. `proposta_enviada` → Simulação enviada
5. `negociacao` → Negociando condições
6. `documentacao` → Colhendo documentos
7. `contratado` → Fechou!
8. `perdido` → Não fechou

**Funcionalidades:**
- Drag-and-drop entre etapas
- Contador por etapa
- Alerta de leads parados (>3 dias)
- Histórico de movimentações
- score automático (0-100)

### C. Gestão de Leads
**Dados do lead:**
- Nome completo, CPF, telefone, email
- Data nascimento, nome da mãe
- Banco benefício, número benefício
- Margem consignável, valor benefício
- Banco atual, valor dívida
- Etapa, score, tags
- Histórico de interações
- Próximas ações
- Vendedor responsável

**Funcionalidades:**
- CRUD completo
- Filtros avanzados (por banco, etapa, score)
- Busca por nome/CPF/telefone
- Importação em massa (Excel)
- Exportação (CSV/Excel)

### D. Chat Coach IA

**O que faz:**
- Responde dúvidas sobre consignado
- Sugere abordagens para cada cliente
- Gera scripts personalizados
- Dá dicas de fechamento
- Treina vendedores em tempo real

**Características:**
- Contexto do vendedor (meta, equipe)
- Histórico da conversa
- Base de conhecimento de consignado
- Sugestões de scripts prontos

### E. Análise de Extrato PDF

**Fluxo:**
1. Vendedor faz upload do PDF
2. IA extrai contratos
3. Identifica oportunidades de portabilidade
4. Calcula economia potencial
5. Detecta contratos que liberam em breve
6. Gera follow-ups automáticos
7. Cria script de venda

**Outputs:**
- Lista de contratos ativos
- Oportunidades imediatas
- Oportunidades futuras (com datas)
- Valor total de economia
- Scripts personalizados
- Follow-ups agendados

### F. WhatsApp Turbinado

**Funcionalidades:**
- Envio individual e em massa
- Templates por etapa
- Botões interativos
- Mensagens com IA personalizada
- Histórico de conversas
- Anti-ban inteligente:
  - Limite 30 msgs/hora
  - Intervalo 20-45s entre envios
  - Mensagens variadas
  - Lista de números bloqueados
  - Circuit breaker para instâncias

### G. Dashboard e Métricas

**Dashboard Vendedor:**
- Conversões do mês (%)
- Comissão acumulada
- Progresso da meta
- Pipeline visual
- Leads atrasados
- Próximas ações (IA prioriza)

**Dashboard Gestor:**
- Visão geral equipe
- Ranking vendedores
- Taxa conversão geral
- Faturamento total
- Redistribuir leads
- Definir metas

### H. Academy (Treinamentos)

**Módulos:**
1. Fundamentos Consignado
2. Portabilidade Master
3. Objeções e Fechamento
4. Análise de Extrato

**Sistema:**
- Quiz após cada módulo
- Certificado digital
- Badge no perfil
- Progresso tracking

---

## 🤖 INTELIGÊNCIA ARTIFICIAL

### Arquitetura dos Agentes

| Agente | Função | Input | Output |
|--------|--------|-------|--------|
| CEO IA | Analisa métricas, sugere estratégias | Dados empresa | Insights, alertas |
| Coach IA | Auxilia vendedores | Mensagem | Resposta + script |
| Supervisor | Monitora pipeline, alerta | DB completo | Alertas, sugestões |
| Analisador | Lê extratos PDF | Arquivo PDF | JSON oportunidades |
| Qualificador | Score de lead | Dados lead | Score + abordagem |

### Prompts Especializados

**Coach IA**:
```
Você é o Coach IA da Paris Cred, especialista em crédito consignado.
Ajude vendedores com:
- Dúvidas sobre produtos
- Como abordar clientes
- Scripts de venda
- Como lidar com objeções
- Melhores práticas

Responda de forma clara, objetiva e motive o vendedor!
```

**Supervisor IA**:
```
Você é o Supervisor IA da Paris Cred. Sua missão é monitorar
o pipeline de vendas e identificar:
- Leads parados há muito tempo
- Gargalos no funil
- Vendedores com performance baixa
- Oportunidades perdidas
- Sugestões de melhoria

Seja proativo e ajude a equipe a vender mais!
```

---

## 🎯 RULES DE NEGÓCIO

### Regras Consignado
- Margem máxima: 30% do benefício líquido
- Prazo máximo: 84 meses (INSS), 72 meses (CLT)
- Taxas médias: 1,5% - 2,5% ao mês
- Portabilidade: após 6 meses do contrato

### Regras do Sistema
- Lead sem contato em 3 dias = alerta
- Follow-up obrigatório após proposta
- Toda interação = registro no histórico
- Vendedor só vê seus leads (isolamento)
- Gestor vê equipe + pode redistribuir
- Admin vê tudo

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Fundação
- [ ] Repositório criado
- [ ] Ambiente configurado
- [ ] Banco de dados schema
- [ ] Auth JWT
- [ ] CRUD usuários

### Fase 2: CRM Core
- [ ] Pipeline Kanban completo
- [ ] CRUD leads completo
- [ ] Dashboard básico
- [ ] Frontend responsivo

### Fase 3: IA
- [ ] Chat Coach funcionando
- [ ] Análise de extrato
- [ ] Supervisor alertas
- [ ] Scripts automáticos

### Fase 4: WhatsApp
- [ ] Integração Evolution
- [ ] Disparos funcionando
- [ ] Anti-ban configurado
- [ ] Templates prontos

### Fase 5: Extra
- [ ] Academy completa
- [ ] Mobile otimizado
- [ ] Deploy online
- [ ] Docs completas

---

## 📊 SUCESSO DO PROJETO

O sistema estará pronto quando:

✅ Vendedor cria lead em < 30 segundos
✅ Pipeline drag-drop funciona suaves
✅ IA responde dúvidas em < 5 segundos
✅ Upload + análise extrato em < 30 segundos
✅ WhatsApp dispara sem bloqueios
✅ Dashboard atualiza em tempo real
✅ Academy com módulos + quizzes
✅ 100% mobile-friendly
✅ Zero bugs críticos
✅ Online 24/7

---

## 💰 INVESTIMENTO (Oportunidade)

Este sistema positioninga a Paris Cred como:
- 🔝 Referência em tecnologia no mercado de consignado
- 🤖 Primeira empresa com IA integrada completa
- 📈 Maior produtividade da equipe
- 💰 Mais conversões e menos custos
- 🏆 Diferencial competitivo imbatível

---

## 🎬 COMEÇAR AGORA

Execute o desenvolvimento faseado, testando cada etapa, garantindo qualidade em cada entrega. O objetivo é ter um sistema funcional em 2-4 semanas e online em 1 mês.

**Próximos passos:**
1. Setup ambiente
2. Banco de dados
3. Auth + Login
4. CRUD Leads
5. Pipeline Kanban
6. Chat IA
7. Análise Extrato
8. WhatsApp
9. Dashboard
10. Deploy

---

*Este é o sistema que vai mudar o mercado de consignado. Vamos construir a versão mais inteligente já criada para a Paris Cred!* 🚀🔥