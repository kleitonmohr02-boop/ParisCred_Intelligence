# Configuração de Serviços - ParisCred Intelligence

## 1. IA - Google Gemini (Gratuito)

### Como obter a API Key:

1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada
5. Cole no arquivo `.env`:
   ```
   GEMINI_API_KEY=sua_chave_aqui
   ```

### Modelo usado:
- **gemini-1.5-flash** - Rápido e gratuito
- Tem créditos gratuitos mensais generosos

### Alternativas (se precisar de mais):
- OpenAI (GPT-3.5) - https://platform.openai.com
- Anthropic (Claude) - https://console.anthropic.com

---

## 2. WhatsApp - Evolution API

### Opção 1: Chat API (Recomendado)
- Site: https://chat-api.com/
- Plano starts: ~R$ 97/mês
- Já inclui instância configurada

### Opção 2: WPPConnect (Gratuito/Self-hosted)
- GitHub: https://github.com/wppconnect-team/wppconnect-server
- Requer servidor VPS próprio
- Gratuito para auto-hospedar

### Opção 3: Evolution API Self-hosted
```bash
# Docker compose
version: '3'
services:
  evolution:
    image: atendai/evolution-api
    ports:
      - "8080:8080"
    environment:
      - SERVER_TYPE=http
      - AUTHENTICATION_API_KEY=sua_chave
```

### Configuração no .env:
```
EVOLUTION_API_URL=http://seu-servidor:8080
EVOLUTION_API_KEY=sua_chave_api
EVOLUTION_INSTANCE_NAME=ParisCred_01
```

---

## 3. Configuração no Render (Produção)

No painel do Render, configure as variáveis de ambiente:

```
FLASK_ENV=production
SECRET_KEY=uma_chave_segura_aqui
GEMINI_API_KEY=sua_chave_gemini
EVOLUTION_API_URL=https://...
EVOLUTION_API_KEY=sua_chave_evolution
```

---

## 4. Testando

Após configurar:
1. Reinicie o servidor
2. Acesse o sistema
3. Envie uma mensagem pelo WhatsApp
4. A IA deve responder automaticamente

Se a IA não responder, verifique os logs em `logs/pariscred.log`
