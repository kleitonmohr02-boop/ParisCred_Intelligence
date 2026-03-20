#!/usr/bin/env python
import traceback
import sys

try:
    from app_novo import app
    print("✅ App carregado com sucesso!")
    
    # Listar todas as rotas registradas
    print("\n📋 Rotas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} → {rule.endpoint}")
    
except Exception as e:
    print(f"❌ Erro ao carregar app: {e}")
    traceback.print_exc()
    sys.exit(1)

# Tentar iniciar servidor
print("\n🚀 Iniciando servidor Flask...")
app.run(debug=False, port=5000, host='0.0.0.0')
