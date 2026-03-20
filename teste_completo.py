#!/usr/bin/env python3
"""Script de teste completo da aplicação"""

import requests
import json

BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_homepage():
    """Testa homepage"""
    print("\n" + "="*60)
    print("🏠 TESTE 1: Homepage")
    print("="*60)
    try:
        response = session.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Homepage carregada com sucesso")
            return True
    except Exception as e:
        print(f"❌ Erro: {e}")
    return False

def test_login_page():
    """Testa página de login"""
    print("\n" + "="*60)
    print("🔐 TESTE 2: Página de Login")
    print("="*60)
    try:
        response = session.get(f"{BASE_URL}/login")
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Página de login acessível")
            return True
    except Exception as e:
        print(f"❌ Erro: {e}")
    return False

def test_dashboard_without_login():
    """Testa acesso a dashboard sem login"""
    print("\n" + "="*60)
    print("🔐 TESTE 3: Proteção de Rotas (sem login)")
    print("="*60)
    try:
        response = session.get(f"{BASE_URL}/dashboard", allow_redirects=False)
        # Se redirecionar para /login, está funcionando corretamente
        if response.status_code in [302, 401]:
            print(f"✅ Redirecionado (Status: {response.status_code})")
            print("✅ Rota protegida funcionando")
            return True
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    return False

def test_api_endpoints():
    """Testa endpoints de API"""
    print("\n" + "="*60)
    print("📡 TESTE 4: Endpoints da API")
    print("="*60)
    
    endpoints = [
        ("/api/campanhas", "GET", "Campanhas"),
        ("/api/admin/usuarios", "GET", "Usuários"),
        ("/api/whatsapp/instancias", "GET", "Instâncias WhatsApp"),
    ]
    
    success_count = 0
    for endpoint, method, name in endpoints:
        try:
            if method == "GET":
                response = session.get(f"{BASE_URL}{endpoint}")
            print(f"   {name}: Status {response.status_code}")
            if response.status_code == 200:
                success_count += 1
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    if success_count == len(endpoints):
        print(f"✅ Todos os endpoints ({success_count}) respondendo")
        return True
    return False

def test_whatsapp_admin_panel():
    """Testa painel WhatsApp do admin"""
    print("\n" + "="*60)
    print("📱 TESTE 5: Painel WhatsApp Admin")
    print("="*60)
    try:
        response = session.get(f"{BASE_URL}/admin/whatsapp")
        print(f"   Status: {response.status_code}")
        if response.status_code in [302, 401]:
            print("⚠️  Requer login (esperado)")
            return True
        elif response.status_code == 200:
            print("✅ Painel WhatsApp acessível")
            return True
    except Exception as e:
        print(f"❌ Erro: {e}")
    return False

def test_vendor_center():
    """Testa Central de Atendimento"""
    print("\n" + "="*60)
    print("👥 TESTE 6: Central de Atendimento (Vendedor)")
    print("="*60)
    try:
        response = session.get(f"{BASE_URL}/vendedor/atendimento")
        print(f"   Status: {response.status_code}")
        if response.status_code in [302, 401]:
            print("⚠️  Requer login (esperado)")
            return True
        elif response.status_code == 200:
            print("✅ Central de Atendimento acessível")
            return True
    except Exception as e:
        print(f"❌ Erro: {e}")
    return False

def run_all_tests():
    """Executa todos os testes"""
    print("\n")
    print("#" * 60)
    print("# 🧪 TESTE COMPLETO DO SISTEMA")
    print("#" * 60)
    
    results = []
    results.append(("Homepage", test_homepage()))
    results.append(("Página Login", test_login_page()))
    results.append(("Proteção Rotas", test_dashboard_without_login()))
    results.append(("Endpoints API", test_api_endpoints()))
    results.append(("Painel WhatsApp", test_whatsapp_admin_panel()))
    results.append(("Central Atendimento", test_vendor_center()))
    
    # Relatório Final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print("\n" + "="*60)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    print("="*60)
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema está OK!")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam. Verifique acima.")

if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
