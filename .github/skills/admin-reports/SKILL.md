---
name: admin-reports
description: "Use when: creating dashboards, generating reports, analyzing KPIs, performance metrics, admin features, data visualization, business intelligence. Handles all administrative and reporting functionality."
---

# 📊 Admin Reports Skill

**Use this skill for**: Dashboards, reports, KPIs, analytics, business intelligence, admin features.

## 📈 KPIs Principais

```python
def calcular_kpis_gerais(data_inicio, data_fim):
    """
    Dashboard executivo com todos os KPIs
    """
    
    # 1. Volume
    total_clientes = db.query("""
        SELECT COUNT(*) as total FROM customers WHERE status != 'bloqueado'
    """)[0][0]
    
    clientes_novos = db.query("""
        SELECT COUNT(*) as total FROM customers 
        WHERE data_criacao BETWEEN ? AND ?
    """, (data_inicio, data_fim))[0][0]
    
    # 2. Financeiro
    total_emprestimos = db.query("""
        SELECT COALESCE(SUM(valor_solicitado), 0) as total
        FROM loans WHERE data_solicitacao BETWEEN ? AND ?
    """, (data_inicio, data_fim))[0][0]
    
    juros_arrecadado = db.query("""
        SELECT COALESCE(SUM(valor_juros), 0) as total
        FROM payments WHERE data_pagamento BETWEEN ? AND ?
        AND status = 'paga'
    """, (data_inicio, data_fim))[0][0]
    
    # 3. Performance
    emprestimos_aprovados = db.query("""
        SELECT COUNT(*) as total FROM loans 
        WHERE status = 'aprovado' AND data_solicitacao BETWEEN ? AND ?
    """, (data_inicio, data_fim))[0][0]
    
    emprestimos_recusados = db.query("""
        SELECT COUNT(*) as total FROM loans 
        WHERE status = 'recusado' AND data_solicitacao BETWEEN ? AND ?
    """, (data_inicio, data_fim))[0][0]
    
    # 4. Risco
    pagamentos_atrasados = db.query("""
        SELECT COUNT(*) as total FROM payments 
        WHERE status = 'atrasada' AND data_vencimento < datetime('now')
    """)[0][0]
    
    inadimplencia_rate = (pagamentos_atrasados / (pagamentos_atrasados + total_emprestimos) * 100) if total_emprestimos > 0 else 0
    
    return {
        "periodo": {"inicio": data_inicio, "fim": data_fim},
        "volume": {
            "total_clientes": total_clientes,
            "clientes_novos": clientes_novos,
            "taxa_crescimento": (clientes_novos / total_clientes * 100) if total_clientes > 0 else 0
        },
        "financeiro": {
            "total_emprestimos": float(total_emprestimos),
            "juros_arrecadado": float(juros_arrecadado),
            "ticket_medio": float(total_emprestimos / emprestimos_aprovados) if emprestimos_aprovados > 0 else 0
        },
        "performance": {
            "emprestimos_aprovados": emprestimos_aprovados,
            "emprestimos_recusados": emprestimos_recusados,
            "taxa_aprovacao": (emprestimos_aprovados / (emprestimos_aprovados + emprestimos_recusados) * 100) if (emprestimos_aprovados + emprestimos_recusados) > 0 else 0
        },
        "risco": {
            "pagamentos_atrasados": pagamentos_atrasados,
            "taxa_inadimplencia": round(inadimplencia_rate, 2)
        }
    }
```

## 📊 Relatórios por Vendedor

```python
def relatorio_vendedor(vendedor_id, data_inicio, data_fim):
    """
    Performance individual de um vendedor
    """
    
    # Propostas criadas
    propostas = db.query("""
        SELECT COUNT(*) as total, SUM(valor) as valor_total
        FROM loans WHERE vendedor_id = ? AND data_solicitacao BETWEEN ? AND ?
    """, (vendedor_id, data_inicio, data_fim))[0]
    
    # Taxa de conversão
    aprovadas = db.query("""
        SELECT COUNT(*) as total FROM loans 
        WHERE vendedor_id = ? AND status = 'aprovado'
        AND data_solicitacao BETWEEN ? AND ?
    """, (vendedor_id, data_inicio, data_fim))[0][0]
    
    # Comissão
    comissao_vendedor = db.query("""
        SELECT COALESCE(SUM(comissao), 0) as total
        FROM vendedor_comissoes
        WHERE vendedor_id = ? AND data BETWEEN ? AND ?
    """, (vendedor_id, data_inicio, data_fim))[0][0]
    
    return {
        "vendedor_id": vendedor_id,
        "periodo": {"inicio": data_inicio, "fim": data_fim},
        "propostas": {
            "total": propostas[0] or 0,
            "valor_total": float(propostas[1] or 0)
        },
        "conversao": {
            "aprovadas": aprovadas,
            "taxa": (aprovadas / propostas[0] * 100) if propostas[0] else 0
        },
        "comissao": float(comissao_vendedor)
    }
```

## 🎯 Relatórios por Canal (WhatsApp, Direct, etc)

```python
def relatorio_canal_atendimento(data_inicio, data_fim):
    """
    Análise de qual canal gera mais conversão
    """
    
    canais = db.query("""
        SELECT 
            tipo_canal,
            COUNT(*) as total_interacoes,
            SUM(CASE WHEN resultado = 'conversao' THEN 1 ELSE 0 END) as conversoes,
            SUM(CASE WHEN resultado = 'conversao' THEN 1 ELSE 0 END) * 100.0 / 
                COUNT(*) as taxa_conversao
        FROM interactions
        WHERE data BETWEEN ? AND ?
        GROUP BY tipo_canal
        ORDER BY conversoes DESC
    """, (data_inicio, data_fim))
    
    return {
        "periodo": {"inicio": data_inicio, "fim": data_fim},
        "canais": [
            {
                "nome": canal[0],
                "total_interacoes": canal[1],
                "conversoes": canal[2],
                "taxa_conversao": round(canal[3], 2)
            }
            for canal in canais
        ]
    }
```

## 💰 Análise de Lucratividade

```python
def analise_lucratividade():
    """
    Margem de lucro e rentabilidade por produto
    """
    
    produtos = db.query("""
        SELECT 
            tipo_produto,
            COUNT(*) as vendas,
            SUM(valor_emprestimo) as valor_total,
            SUM(valor_juros) as juros_total,
            SUM(custo_operacional) as custo_total,
            AVG(margem_lucrativa) as margem_media
        FROM loans
        WHERE status = 'pago'
        GROUP BY tipo_produto
    """)
    
    resultado = []
    for produto in produtos:
        lucro_bruto = produto[3] - produto[4]
        margem_bruta = (lucro_bruto / produto[2] * 100) if produto[2] > 0 else 0
        
        resultado.append({
            "produto": produto[0],
            "vendas": produto[1],
            "valor_total": float(produto[2]),
            "juros": float(produto[3]),
            "custo_operacional": float(produto[4]),
            "lucro_bruto": float(lucro_bruto),
            "margem_bruta_%": round(margem_bruta, 2)
        })
    
    return {
        "data_relatorio": datetime.now().isoformat(),
        "produtos": resultado
    }
```

## 📱 Dashboard Widget - Últimas Transações

```python
def ultimas_transacoes(limite=10):
    """
    Widget para dashboard com transações recentes
    """
    transacoes = db.query("""
        SELECT 
            l.id,
            c.name,
            l.valor_solicitado,
            l.status,
            l.data_solicitacao
        FROM loans l
        JOIN customers c ON l.customer_id = c.id
        ORDER BY l.data_solicitacao DESC
        LIMIT ?
    """, (limite,))
    
    return [
        {
            "id": t[0],
            "cliente": t[1],
            "valor": float(t[2]),
            "status": t[3],
            "data": t[4]
        }
        for t in transacoes
    ]
```

## 🔔 Alertas Automáticos

```python
def verificar_alertas():
    """
    Dispara alertas para admin
    """
    alertas = []
    
    # 1. Taxa de inadimplência muito alta
    taxa_inadimplencia = calcular_taxa_inadimplencia()
    if taxa_inadimplencia > 5:
        alertas.append({
            "tipo": "ALERTA",
            "mensagem": f"Taxa de inadimplência em {taxa_inadimplencia}%",
            "acao": "Revisar políticas de concessão"
        })
    
    # 2. Vendedor com desempenho baixo
    vendedor_pior = obter_pior_vendedor()
    if vendedor_pior['taxa_conversao'] < 10:
        alertas.append({
            "tipo": "AVISO",
            "mensagem": f"Vendedor {vendedor_pior['nome']} com taxa de conversão baixa",
            "acao": f"Retraining necessário"
        })
    
    # 3. Servidor WhatsApp offline
    instancias_offline = contar_instancias_offline()
    if instancias_offline > 0:
        alertas.append({
            "tipo": "CRÍTICO",
            "mensagem": f"{instancias_offline} instâncias WhatsApp offline",
            "acao": "Reconectar imediatamente"
        })
    
    return alertas
```

## 📊 Template Dashboard HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>ParisCred - Dashboard Admin</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="dashboard">
        <!-- KPIs -->
        <div class="kpi-container">
            <div class="kpi">
                <h3>Clientes Ativos</h3>
                <p id="total-clientes" class="kpi-value">0</p>
            </div>
            <div class="kpi">
                <h3>Empréstimos Este Mês</h3>
                <p id="emprestimos-mes" class="kpi-value">R$ 0</p>
            </div>
            <div class="kpi">
                <h3>Taxa de Inadimplência</h3>
                <p id="inadimplencia" class="kpi-value">0%</p>
            </div>
        </div>
        
        <!-- Gráficos -->
        <div id="grafico-vendas"></div>
        <div id="grafico-canais"></div>
        <div id="ultimas-transacoes"></div>
    </div>
    
    <script>
        // Carregar dados via API
        fetch('/api/admin/kpis').then(r => r.json()).then(data => {
            document.getElementById('total-clientes').textContent = data.volume.total_clientes;
            document.getElementById('emprestimos-mes').textContent = 'R$ ' + data.financeiro.total_emprestimos.toFixed(2);
            document.getElementById('inadimplencia').textContent = data.risco.taxa_inadimplencia.toFixed(2) + '%';
        });
    </script>
</body>
</html>
```

## ✅ Checklist

- [ ] KPIs calculam corretamente
- [ ] Relatórios por vendedor
- [ ] Análise de canais
- [ ] Dashboard HTML responsivo
- [ ] Gráficos interativos
- [ ] Alertas automáticos
- [ ] Export PDF/CSV
- [ ] Agendamento de relatórios
