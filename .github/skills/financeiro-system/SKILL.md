---
name: financeiro-system
description: "Use when: calculating loans, simulating consignado scenarios, financial reports, payment schedules, interest calculations, debt analysis, risk assessment. Handles all financial operations and calculations."
---

# 💰 Financeiro System Skill

**Use this skill for**: Loan calculations, simulations, financial reports, payment schedules, interest, debt, risk metrics.

## 🧮 Fórmulas Principais

### Cálculo de Consignado
```python
def calcular_consignado(renda_liquida, percentual_margem=30):
    """
    Calcula o máximo que pode ser consignado
    """
    margem_consignavel = renda_liquida * (percentual_margem / 100)
    return {
        "renda_liquida": renda_liquida,
        "percentual_margem": percentual_margem,
        "margem_consignavel": margem_consignavel
    }

# Exemplo
resultado = calcular_consignado(5000, 30)
# {
#     "renda_liquida": 5000,
#     "percentual_margem": 30,
#     "margem_consignavel": 1500
# }
```

### Simulação de Empréstimo
```python
def simular_emprestimo(valor_solicitado, taxa_juros_anual, num_parcelas):
    """
    Simula um empréstimo com juros
    
    Entrada:
    - valor_solicitado: float (ex: 5000)
    - taxa_juros_anual: float (ex: 2.5)
    - num_parcelas: int (ex: 60)
    
    Retorna: Cronograma completo
    """
    taxa_mensal = taxa_juros_anual / 100 / 12
    
    if taxa_mensal == 0:
        parcela_mensal = valor_solicitado / num_parcelas
    else:
        parcela_mensal = valor_solicitado * (taxa_mensal * (1 + taxa_mensal)**num_parcelas) / \
                        ((1 + taxa_mensal)**num_parcelas - 1)
    
    cronograma = []
    saldo_restante = valor_solicitado
    juros_total = 0
    
    for i in range(1, num_parcelas + 1):
        juros_parcela = saldo_restante * taxa_mensal
        amortizacao = parcela_mensal - juros_parcela
        saldo_restante -= amortizacao
        juros_total += juros_parcela
        
        cronograma.append({
            "parcela": i,
            "valor_parcela": round(parcela_mensal, 2),
            "amortizacao": round(amortizacao, 2),
            "juros": round(juros_parcela, 2),
            "saldo_devedor": round(max(0, saldo_restante), 2)
        })
    
    return {
        "valor_original": valor_solicitado,
        "taxa_juros_anual": taxa_juros_anual,
        "numero_parcelas": num_parcelas,
        "valor_parcela": round(parcela_mensal, 2),
        "valor_total_pago": round(parcela_mensal * num_parcelas, 2),
        "juros_total": round(juros_total, 2),
        "cronograma": cronograma
    }
```

### Análise de Risco
```python
def analisar_risco(cliente_data):
    """
    Classifica cliente em categorias de risco: BAIXO, MÉDIO, ALTO
    """
    renda = cliente_data['renda']
    valor_solicitado = cliente_data['valor_solicitado']
    historico_pagamentos = cliente_data.get('historico_pagamentos', [])
    
    # Indicador 1: Renda vs Valor Solicitado
    razao_divida = valor_solicitado / renda if renda > 0 else 9999
    
    # Indicador 2: Histórico
    atrasos = sum(1 for p in historico_pagamentos if not p['pago_no_prazo'])
    taxa_inadimplencia = atrasos / len(historico_pagamentos) if historico_pagamentos else 0
    
    # Indicador 3: Idade
    idade = cliente_data.get('idade', 40)
    
    # Score
    score = 0
    score += min(razao_divida * 35, 35)  # Até 35 pontos
    score += min(taxa_inadimplencia * 40, 40)  # Até 40 pontos
    score += max(70 - idade, 0) * 0.25  # Até 7.5 pontos
    
    if score < 30:
        risco = "BAIXO"
    elif score < 60:
        risco = "MÉDIO"
    else:
        risco = "ALTO"
    
    return {
        "score": round(score, 2),
        "risco": risco,
        "razao_divida": round(razao_divida, 2),
        "inadimplencia": round(taxa_inadimplencia * 100, 2)
    }
```

## 📊 Database Schema - Financeiro

```python
# loans table
- id: INTEGER PRIMARY KEY
- customer_id: FOREIGN KEY
- valor_solicitado: DECIMAL
- taxa_juros_anual: DECIMAL
- num_parcelas: INTEGER
- status: TEXT (aprovado, pendente, recusado, pago)
- data_solicitacao: TIMESTAMP
- data_aprovacao: TIMESTAMP
- data_vencimento: TIMESTAMP

# payments table
- id: INTEGER PRIMARY KEY
- loan_id: FOREIGN KEY
- numero_parcela: INTEGER
- valor_parcela: DECIMAL
- valor_juros: DECIMAL
- data_vencimento: TIMESTAMP
- data_pagamento: TIMESTAMP
- status: TEXT (paga, pendente, atrasada)

# financial_metrics table
- id: INTEGER PRIMARY KEY
- data: TIMESTAMP
- total_emprestimos: DECIMAL
- total_juros_arrecadado: DECIMAL
- emprestimos_ativos: INTEGER
- emprestimos_atrasados: INTEGER
```

## 📈 Relatórios Financeiros

### Dashboard Executivo
```python
def dashboard_financeiro(data_inicio, data_fim):
    return {
        "receita_total": sum_juros(data_inicio, data_fim),
        "emprestimos_novos": count_loans(data_inicio, data_fim),
        "taxa_inadimplencia": calc_inadimplencia(),
        "valor_medio_emprestimo": avg_loan(),
        "top_produtos": top_selling_products()
    }
```

## ✅ Integração com Vendedor

Quando vendedor cria proposta:
1. Simular empréstimo
2. Calcular margem disponível
3. Analisar risco
4. Gerar cronograma
5. Salvar proposta no banco
6. Enviar para cliente via WhatsApp

## 🛡️ Regras de Negócio

- Cliente deve ter renda >= R$ 1.000
- Margem consignável máxima = 30% da renda
- Taxa de juros entre 1% a 10% a.a.
- Mínimo 12 parcelas, máximo 84 parcelas
- Clientes com 2+ inadimplências → análise especial

## ✅ Checklist

- [ ] Cálculos de consignado funcionando
- [ ] Simulador de empréstimo preciso
- [ ] Análise de risco implementada
- [ ] Cronograma de pagamentos
- [ ] Relatórios financeiros
- [ ] Integração com salesforce/CRM
