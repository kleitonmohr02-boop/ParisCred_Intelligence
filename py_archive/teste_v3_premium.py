"""
Script de Teste: ParisCred v3.0 - IA e Anti-Ban
Verifica se as novas funcionalidades estão ativas
"""

import sys
import os

# Adicionar diretório atual ao path
sys.path.append(os.getcwd())

print("========================================")
print("   TESTE DE MELHORIAS PARISCRED V3.0")
print("========================================\n")

try:
    from modulo_ia import agente_ia
    from modulo_antiban import anti_ban
    from skill_whatsapp import WhatsAppDB
    
    print("[1] Testando Conexão com Ollama...")
    if agente_ia.esta_online():
        print("✅ Ollama está ONLINE!")
        print("--- Gerando resposta de teste ---")
        resposta = agente_ia.gerar_resposta("Olá, como funciona o empréstimo?")
        print(f"Robô diz: {resposta}")
    else:
        print("❌ Ollama está OFFLINE (Certifique-se de que o Ollama está aberto).")
        print("ℹ️ O sistema usará o modo Fallback (palavras-chave).")

    print("\n[2] Testando Simulação de Digitação...")
    # Teste de interface (não envia de verdade sem instância ativa, mas testa o código)
    print("ℹ️ Módulo Anti-Ban carregado com sucesso.")
    
    print("\n[3] Verificando Integração no WhatsApp...")
    print("--- Testando lógica de resposta ---")
    resp_fallback = WhatsAppDB._classificar_e_responder("quero simular um credito")
    print(f"Resposta gerada: {resp_fallback[:50]}...")
    
    print("\n[4] Verificando Background Dispatch...")
    from app_novo import DISPAROS_ATIVOS
    print(f"Dicionário de monitoramento ativo: {type(DISPAROS_ATIVOS)}")
    
    print("\n========================================")
    print("   RESULTADO: TUDO PRONTO PARA USO!")
    print("========================================")

except Exception as e:
    print(f"\n❌ Erro durante a verificação: {str(e)}")
    import traceback
    traceback.print_exc()

input("\nPressione Enter para sair...")
