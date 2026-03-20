---
name: crm-management
description: "Use when: creating or managing customers, leads, CRM data, client journeys, customer relationships, contact management. Handles all customer-related operations in ParisCred including data models, CRUD operations, and integrations."
---

# 🤝 CRM Management Skill

**Use this skill for**: Customer management, leads, client data, relationships, contact history, customer profiles.

## 📊 Database Schema

```python
# customers table
- id: INTEGER PRIMARY KEY
- name: TEXT
- email: TEXT
- phone: TEXT
- cpf: TEXT UNIQUE
- status: TEXT (ativo, inativo, lead)
- data_criacao: TIMESTAMP
- valor_limite_consignado: DECIMAL
- empresa: TEXT
- cargo: TEXT
- renda: DECIMAL
- margem_consignavel: DECIMAL
- custom_fields: JSON

# interactions table
- id: INTEGER PRIMARY KEY
- customer_id: FOREIGN KEY
- tipo: TEXT (chamada, whatsapp, email, visita)
- descricao: TEXT
- data: TIMESTAMP
```

## 🔧 Operações Comuns

### Criar Cliente
```python
def criar_cliente(name, email, phone, cpf, empresa, cargo, renda):
    # Validar CPF
    if not validar_cpf(cpf):
        return {"erro": "CPF inválido"}
    
    # Verificar duplicado
    cliente_existente = db.query("SELECT id FROM customers WHERE cpf = ?", (cpf,))
    if cliente_existente:
        return {"erro": "Cliente já existe"}
    
    # Calcular margem consignável
    margem = renda * 0.30  # 30% padrão
    
    # Inserir
    db.execute("""
        INSERT INTO customers (name, email, phone, cpf, empresa, cargo, renda, margem_consignavel, status, data_criacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'lead', datetime('now'))
    """, (name, email, phone, cpf, empresa, cargo, renda, margem))
    
    return {"sucesso": True, "cliente_id": db.lastrowid}
```

### Listar Clientes com Filtros
```python
def listar_clientes(status='ativo', limite=None, offset=0):
    query = "SELECT * FROM customers WHERE status = ?"
    params = [status]
    
    if limite:
        query += " LIMIT ? OFFSET ?"
        params.extend([limite, offset])
    
    clientes = db.query(query, tuple(params))
    return clientes
```

### Atualizar Status Cliente
```python
def atualizar_status_cliente(cliente_id, novo_status):
    # Status válidos: lead, ativo, inativo, bloqueado
    status_validos = ['lead', 'ativo', 'inativo', 'bloqueado']
    
    if novo_status not in status_validos:
        return {"erro": f"Status deve ser um de: {status_validos}"}
    
    db.execute("UPDATE customers SET status = ? WHERE id = ?", (novo_status, cliente_id))
    return {"sucesso": True}
```

### Registrar Interação
```python
def registrar_interacao(cliente_id, tipo, descricao):
    db.execute("""
        INSERT INTO interactions (customer_id, tipo, descricao, data)
        VALUES (?, ?, ?, datetime('now'))
    """, (cliente_id, tipo, descricao))
    return {"sucesso": True}
```

## 📈 Relatórios CRM

### Clientes por Status
```python
def relatorio_clientes_por_status():
    resultado = db.query("""
        SELECT status, COUNT(*) as total, 
               SUM(margem_consignavel) as margem_total
        FROM customers
        GROUP BY status
    """)
    return resultado
```

### Top Clientes por Renda
```python
def top_clientes_renda(limite=10):
    return db.query("""
        SELECT id, name, renda, margem_consignavel, email, phone
        FROM customers
        WHERE status = 'ativo'
        ORDER BY renda DESC
        LIMIT ?
    """, (limite,))
```

## 🔗 Integração WhatsApp

Quando um cliente interage via WhatsApp:
1. Verificar/criar registro em customers
2. Registrar interação
3. Atualizar última_interacao timestamp
4. Classificar automaticamente

## ✅ Checklist para Implementação

- [ ] Schema do banco criado
- [ ] Validações de CPF
- [ ] CRUD completo
- [ ] Relatórios básicos
- [ ] Integração WhatsApp
- [ ] Sincronização com Evolution API
