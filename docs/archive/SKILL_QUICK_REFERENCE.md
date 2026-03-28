# 📋 GUIA RÁPIDO - SUPER COPILOT SKILLS

## 🎯 5 Skills à seu Disposal

### 1️⃣ **CRM Management** - Gestão de Clientes
```
Use quando: trabalhar com clientes, leads, histórico
Comando: /crm

Exemplo:
"Cria função pra listar clientes ativos"
"Implementa busca por CPF"
"Integra novo cliente com WhatsApp"
"Gera relatório de clientes por status"
```

**Templates Disponíveis**:
- ✅ Validação CPF
- ✅ Cálculo Margem Consignável
- ✅ CRUD Completo
- ✅ Integração WhatsApp
- ✅ Relatórios de Cliente

---

### 2️⃣ **Financeiro System** - Cálculos & Simulações
```
Use quando: precisa de números, cálculos, simulações
Comando: /financeiro

Exemplo:
"Simula empréstimo de R$ 5000 em 60x"
"Calcula margem consignável"
"Verifica risco do cliente"
"Gera cronograma de pagamento"
"Relatório de lucratividade"
```

**Templates Disponíveis**:
- ✅ Simulador de Empréstimo
- ✅ Cálculo de Consignado
- ✅ Análise de Risco
- ✅ Cronograma de Pagamentos
- ✅ KPIs Financeiros

---

### 3️⃣ **WhatsApp Atendimento** - Automação WhatsApp
```
Use quando: trabalhar com WhatsApp, automação, chatbot
Comando: /whatsapp

Exemplo:
"Conecta número na Evolution API"
"Cria ChatBot de atendimento"
"Automação maturador de números"
"Dispara campanhas em massa"
"Webhook pra receber mensagens"
```

**Templates Disponíveis**:
- ✅ Conexão WhatsApp (QR Code)
- ✅ Envio de Mensagens
- ✅ Chatbot Flow
- ✅ Webhook Handler
- ✅ Maturador de Números

---

### 4️⃣ **Admin Reports** - Dashboards & Relatórios
```
Use quando: precisa de dados, análises, relatórios
Comando: /admin

Exemplo:
"Cria dashboard com KPIs"
"Relatório de vendedor"
"Análise por canal"
"Lucratividade por produto"
"Alertas automáticos"
```

**Templates Disponíveis**:
- ✅ KPIs Gerais
- ✅ Performance Vendedor
- ✅ Análise de Canais
- ✅ Lucratividade
- ✅ Alertas Automáticos

---

## 🔌 MCP SERVERS - Acesso Direto

### Evolution API
```
O quê: Controlar números WhatsApp
Quando: Precisa gerenciar instâncias, enviar mensagens
Como: Automático quando usa /whatsapp

Ferramentas:
- create_whatsapp_instance()
- list_whatsapp_instances()
- send_whatsapp_message()
- get_instance_status()
```

### ParisCred Database
```
O quê: Acessar dados do banco SQLite
Quando: Precisa buscar/salvar dados
Como: Automático em cualquer operação de dados

Ferramentas:
- execute_query() - SELECT
- execute_insert_update() - INSERT/UPDATE/DELETE
- get_table_schema() - Estrutura
- list_tables() - Tabelas
```

---

## 💻 Exemplos de Uso Real

### Cenário 1: Novo Cliente
```
Você: "Cria fluxo pra novo cliente via WhatsApp"

Eu uso:
  1. /crm (template cadastro cliente)
  2. /whatsapp (enviar msg boas-vindas)
  3. database-mcp (salvar no banco)
  
Resultado: Fluxo completo em Python/Code
```

### Cenário 2: Relatório de Vendas
```
Você: "Me mostra a performance do João em março"

Eu uso:
  1. database-mcp (query dados do João)
  2. /financeiro (calcula comissão)
  3. /admin (formata relatório)
  4. mcp-evolution (mensagem WhatsApp com resultado)
  
Resultado: Dados + Gráfico + Enviado WhatsApp
```

### Cenário 3: Campanha WhatsApp
```
Você: "Cria campanha pra ofertar empréstimo a clientes ativos"

Eu uso:
  1. database-mcp (listar ativos)
  2. /financeiro (gerar oferta personalizada)
  3. /whatsapp (template + webhook)
  4. evolution-mcp (enviar em massa)
  
Resultado: Sistema automático pronto
```

---

## 🎓 Tips de Uso

### ✅ Melhor Forma
```
"Implementa busca de clientes por CPF no database"
→ Retorno: Código pronto com validação + erro handling
```

### ❌ Forma Vaga
```
"Como eu faço busca?"
→ Retorno: Genérico, sem contexto do projeto
```

### ✅ Especifique o Que Quer
```
"Usa a skill /crm pra criar função de busca"
→ Retorno: Com template CRM pronto
```

### ✅ Peça Integrações
```
"Integra busca de cliente com WhatsApp"
→ Retorno: /crm + /whatsapp + evolução-mcp
```

---

## 📞 Atalhos Úteis

| Você diz | Eu faço |
|----------|---------|
| "Topo de vendedores" | Query + /admin |
| "Qual taxa de inadimplência?" | Query + /financeiro |
| "Cria chatbot" | /whatsapp + template |
| "Próximos atrasados" | database-mcp + alerta |
| "Simula 5x melhor caso" | /financeiro + 5 scenarios |
| "Conecta novo WhatsApp" | /whatsapp + evolution-mcp |

---

## 🚨 Importante

- Skills trabalham em **conjunto** (não exclusivamente)
- MCP Servers são **automáticos** (não precisa ativar)
- Sempre peço confirmação pra mudanças **críticas**
- Database é **seguro** (apenas SELECT por padrão)

---

## 📍 Próximo Passo

Você: **"Vamos começar com o projeto"**

Eu vou:
1. Explorar estrutura completa
2. Aprender suas convenções
3. Começar a usar as skills
4. Trabalhar em tarefas reais

🚀 **BORA?**
