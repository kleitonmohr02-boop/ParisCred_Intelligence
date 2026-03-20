"""
🔑 ONDE OBTER A API KEY - EVOLUTION API

A chave API é gerada no seu DASHBOARD da Evolution API.
Siga estes passos:
"""

print("""
════════════════════════════════════════════════════════════════════════════════
                    🔑 COMO OBTER SUA API KEY
════════════════════════════════════════════════════════════════════════════════

OPÇÃO 1️⃣: NO DASHBOARD EVOLUTION API
──────────────────────────────────────────────────────────────────────────────

1. Acesse: https://app.evolution-api.com/ (ou o URL do seu servidor)

2. Faça LOGIN com suas credenciais

3. No menu lateral, procure por:
   • "API Key" ou
   • "Chaves de Acesso" ou  
   • "Settings" → "API Keys"

4. Clique em "Copiar" ou "Gerar Nova Chave" se não tiver uma

5. A chave deve parecer algo como:
   ➜ 4f1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o

──────────────────────────────────────────────────────────────────────────────

OPÇÃO 2️⃣: VIA LINHA DE COMANDO (Se estiver rodando Evolution localmente)
──────────────────────────────────────────────────────────────────────────────

Se você está rodando Evolution API em Docker, a chave pode estar nas logs:

docker logs evolution-api | grep -i "api" | grep -i "key"

Ou procure no arquivo de configuração do Docker:
cat docker-compose.yml | grep GLOBAL_API_KEY

──────────────────────────────────────────────────────────────────────────────

OPÇÃO 3️⃣: TESTAR CONFIGURAÇÃO (após adicionar a chave)
──────────────────────────────────────────────────────────────────────────────

Após adicionar a chave no config.py, execute:

python tester.py

Se funcionar, você verá:
✓ API está ONLINE!
✓ Versão: 2.2.3

════════════════════════════════════════════════════════════════════════════════

📝 PRÓXIMOS PASSOS:

1. Encontre sua API Key (uma das opções acima)

2. Abra o arquivo config.py:

   EVOLUTION_URL = 'http://localhost:8080'
   GLOBAL_API_KEY = 'COLE_SUA_CHAVE_AQUI'  ← SUBSTITUA ISTO
   DELAY_MIN = 20
   DELAY_MAX = 60

3. Salve o arquivo (Ctrl+S)

4. Execute:

   python auto_setup.py

════════════════════════════════════════════════════════════════════════════════

⚠️ IMPORTANTE:

• Nunca compartilhe sua API Key com ninguém
• Mantenha ela segura (não comete em repositório público)
• Se vazar, regenere uma nova chave no dashboard

════════════════════════════════════════════════════════════════════════════════
""")

# Tenta detectar se é Docker
import subprocess
import sys

print("\n🔍 Verificando se você está em um ambiente Docker...\n")

try:
    resultado = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=2)
    
    if 'evolution' in resultado.stdout.lower():
        print("✓ Docker detectado com Evolution API rodando!")
        print("\nTentando extrair API Key das logs:\n")
        
        try:
            logs = subprocess.run(
                ['docker', 'logs', 'evolution-api'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Procura por padrões de API Key
            for linha in logs.stdout.split('\n'):
                if 'api' in linha.lower() and ('key' in linha.lower() or 'secret' in linha.lower()):
                    print(f"  → {linha[:100]}")
                    
        except Exception as e:
            print(f"  ⚠️  Não consegui acessar logs: {e}")
            
    else:
        print("ℹ️  Docker não detectado ou Evolution não está em containers visíveis.")
        
except Exception as e:
    print(f"ℹ️  Docker não parece estar instalado ou ativo.")

print("\n" + "=" * 70)
print("💡 Dica: Se você é iniciante, peça a chave ao administrador do servidor")
print("=" * 70 + "\n")
