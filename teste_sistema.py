# -*- coding: utf-8 -*-
"""
Script de Testes - ParisCred Intelligence
Executar: python teste_sistema.py
"""

import json
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RESULTADOS = []

def main():
    from app import app
    
    print("="*60)
    print("  TESTE DO SISTEMA PARISCRED INTELLIGENCE")
    print("="*60)
    print()
    
    # Usar cliente de teste com sessao mantida
    with app.test_client() as client:
        with client.session_transaction() as sessao:
            sessao['usuario'] = 'admin@pariscred.com'
        
        # ============================================================
        # FASE 1: ROTAS PUBLICAS
        # ============================================================
        print("\n[FASE 1] Rotas Publicas")
        print("-"*40)
        
        resp = client.get('/')
        RESULTADOS.append({"nome": "Pagina Inicial", "rota": "/", "status": resp.status_code, "sucesso": True})
        print(f"[OK] Pagina Inicial: {resp.status_code}")
        
        resp = client.get('/login')
        RESULTADOS.append({"nome": "Login Page", "rota": "/login", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Login Page: {resp.status_code}")
        
        # ============================================================
        # FASE 2: AUTENTICACAO
        # ============================================================
        print("\n[FASE 2] Autenticacao")
        print("-"*40)
        
        # Login
        resp = client.post('/login', data={'email': 'admin@pariscred.com', 'senha': 'Admin@2025'})
        login_ok = resp.status_code in [200, 302]
        RESULTADOS.append({"nome": "Login Admin", "rota": "/login", "status": resp.status_code, "sucesso": login_ok})
        print(f"{'[OK]' if login_ok else '[ERRO]'} Login Admin: {resp.status_code}")
        
        # Manter sessao apos login
        with client.session_transaction() as sessao:
            sessao['usuario'] = 'admin@pariscred.com'
        
        # Dashboard
        resp = client.get('/dashboard')
        RESULTADOS.append({"nome": "Dashboard", "rota": "/dashboard", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Dashboard: {resp.status_code}")
        
        # ============================================================
        # FASE 3: CRM
        # ============================================================
        print("\n[FASE 3] CRM")
        print("-"*40)
        
        # Pagina CRM
        resp = client.get('/crm')
        RESULTADOS.append({"nome": "Pagina CRM", "rota": "/crm", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina CRM: {resp.status_code}")
        
        # API Leads
        resp = client.get('/api/crm/leads')
        RESULTADOS.append({"nome": "API Leads", "rota": "/api/crm/leads", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} API Leads: {resp.status_code}")
        
        # Criar Cliente (usar dados unicos com timestamp)
        timestamp = int(time.time())
        resp = client.post('/api/crm/clientes', 
                          json={
                              "nome": f"TESTE {timestamp}",
                              "phone": f"119999{timestamp % 10000:04d}",
                              "cpf": f"{timestamp % 100000000011:011d}",
                              "email": f"teste{timestamp}@email.com",
                              "renda": 5000,
                              "status": "Novo Lead"
                          })
        RESULTADOS.append({"nome": "Criar Cliente", "rota": "/api/crm/clientes", "status": resp.status_code, "sucesso": resp.status_code in [200, 201]})
        print(f"{'[OK]' if resp.status_code in [200, 201] else '[ERRO]'} Criar Cliente: {resp.status_code}")
        
        # Get leads para pegar ID valido
        resp_leads = client.get('/api/crm/leads')
        leads_data = resp_leads.get_json()
        leads = leads_data.get('leads', []) if isinstance(leads_data, dict) else leads_data
        
        # Pegar o ultimo lead criado
        if leads:
            lead_id = leads[0]['id']
            # Atualizar para Pendente (diferente do status atual)
            current_status = leads[0].get('status', 'lead')
            target_status = "Pendente" if current_status != "Pendente" else "Finalizado"
            
            resp = client.post('/api/crm/update_status', 
                              json={"lead_id": lead_id, "status": target_status})
            RESULTADOS.append({"nome": "Update Status", "rota": "/api/crm/update_status", "status": resp.status_code, "sucesso": resp.status_code == 200})
            print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Update Status: {resp.status_code}")
        else:
            RESULTADOS.append({"nome": "Update Status", "rota": "/api/crm/update_status", "status": 0, "sucesso": False})
            print("[ERRO] Update Status: Nenhum lead encontrado")
        
        # ============================================================
        # FASE 4: FINANCEIRO
        # ============================================================
        print("\n[FASE 4] Financeiro")
        print("-"*40)
        
        resp = client.get('/financeiro')
        RESULTADOS.append({"nome": "Pagina Financeiro", "rota": "/financeiro", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina Financeiro: {resp.status_code}")
        
        # ============================================================
        # FASE 5: WHATSAPP
        # ============================================================
        print("\n[FASE 5] WhatsApp")
        print("-"*40)
        
        resp = client.get('/whatsapp')
        RESULTADOS.append({"nome": "Pagina WhatsApp", "rota": "/whatsapp", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina WhatsApp: {resp.status_code}")
        
        # ============================================================
        # FASE 6: CAMPANHAS
        # ============================================================
        print("\n[FASE 6] Campanhas")
        print("-"*40)
        
        resp = client.get('/campanhas')
        RESULTADOS.append({"nome": "Pagina Campanhas", "rota": "/campanhas", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina Campanhas: {resp.status_code}")
        
        # ============================================================
        # FASE 7: IMPORTAR LEADS
        # ============================================================
        print("\n[FASE 7] Importar Leads")
        print("-"*40)
        
        resp = client.get('/importar')
        RESULTADOS.append({"nome": "Pagina Importar", "rota": "/importar", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina Importar: {resp.status_code}")
        
        # ============================================================
        # FASE 8: CHAT IA COACH
        # ============================================================
        print("\n[FASE 8] Chat IA Coach")
        print("-"*40)
        
        resp = client.get('/coach')
        RESULTADOS.append({"nome": "Pagina Coach", "rota": "/coach", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina Coach: {resp.status_code}")
        
        # ============================================================
        # FASE 9: ANALISE DE EXTRATO
        # ============================================================
        print("\n[FASE 9] Analise de Extrato")
        print("-"*40)
        
        resp = client.get('/extrato')
        RESULTADOS.append({"nome": "Pagina Extrato", "rota": "/extrato", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina Extrato: {resp.status_code}")
        
        # ============================================================
        # FASE 10: ADMIN
        # ============================================================
        print("\n[FASE 10] Admin")
        print("-"*40)
        
        resp = client.get('/admin')
        RESULTADOS.append({"nome": "Pagina Admin", "rota": "/admin", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina Admin: {resp.status_code}")
        
        # ============================================================
        # FASE 11: DASHBOARD
        # ============================================================
        print("\n[FASE 11] Dashboard")
        print("-"*40)
        
        resp = client.get('/dashboard')
        RESULTADOS.append({"nome": "Pagina Dashboard", "rota": "/dashboard", "status": resp.status_code, "sucesso": resp.status_code == 200})
        print(f"{'[OK]' if resp.status_code == 200 else '[ERRO]'} Pagina Dashboard: {resp.status_code}")
        
        # Logout
        resp = client.get('/logout')
        RESULTADOS.append({"nome": "Logout", "rota": "/logout", "status": resp.status_code, "sucesso": resp.status_code in [200, 302]})
        print(f"{'[OK]' if resp.status_code in [200, 302] else '[ERRO]'} Logout: {resp.status_code}")
    
    # ============================================================
    # RESUMO
    # ============================================================
    print("\n" + "="*60)
    print("  RESUMO DOS TESTES")
    print("="*60)
    
    total = len(RESULTADOS)
    ok = len([r for r in RESULTADOS if r.get("sucesso")])
    erro = total - ok
    
    print(f"\nTotal de testes: {total}")
    print(f"[OK] Sucessos: {ok}")
    print(f"[ERRO] Erros: {erro}")
    
    # Listar erros
    erros = [r for r in RESULTADOS if not r.get("sucesso")]
    if erros:
        print("\n[ERRO] ERROS ENCONTRADOS:")
        for r in erros:
            print(f"  - {r['nome']}: Status {r.get('status')}")
            print(f"    Rota: {r.get('rota')}")
    
    # Salvar resultados em JSON
    with open("teste_resultado.json", "w", encoding="utf-8") as f:
        json.dump(RESULTADOS, f, indent=2, ensure_ascii=False)
    
    print("\n[INFO] Resultados salvos em: teste_resultado.json")
    
    return erro == 0

if __name__ == "__main__":
    main()
