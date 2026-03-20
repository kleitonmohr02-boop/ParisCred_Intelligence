# ✅ CHECKLIST: CONECTAR WHATSAPP

## 📋 O QUE VOCÊ PRECISA FAZER AGORA (MANUALMENTE)

### Pré-requisitos
- [ ] Telefone com WhatsApp instalado
- [ ] Evolution API rodando (localhost:8080)
- [ ] 3 números de WhatsApp disponíveis (podem ser do mesmo chip)
- [ ] WiFi conectado

---

## 🔄 FLUXO COMPLETO

### ETAPA 1️⃣: CRIAR INSTÂNCIAS (Automático)

Execute:
```bash
cd C:\ParisCred_Intelligence
python CONECTAR_WHATSAPP.py
```

Isso vai:
- ✓ Tentar criar 3 instâncias no Evolution
- ✓ Gerar QR Codes
- ✓ Validar status

### ETAPA 2️⃣: ESCANEAR QR CODES (Manual)

**Para CADA instância (Paris_01, Chip01, Chip02):**

1. Pegue seu telefone
2. Abra **WhatsApp**
3. Vá em **⋮ Configurações**
4. Clique em **"Aparelhos conectados"** (ou "Devices")
5. Toque em **"Conectar um aparelho"** (ou "Link a device")
6. Aponte câmera para o **QR Code** que aparecer na tela
7. Aguarde aparecer ✓ **Conectado**

### ETAPA 3️⃣: VALIDAR CONEXÃO (Automático)

O script vai verificar se cada uma está conectada.

---

## 🎯 RESULTADO ESPERADO

Após conectar as 3:

```
✓ Paris_01  → Conectada
✓ Chip01    → Conectada  
✓ Chip02    → Conectada
```

---

## 🧪 TESTE FINAL

Uma vez conectadas, as instâncias aparecerão assim no dashboard:

```
📱 Instâncias Ativas:

Paris_01   ✓ Online  | Último acesso: agora
Chip01     ✓ Online  | Último acesso: agora
Chip02     ✓ Online  | Último acesso: agora
```

---

## ⚠️ SE ALGO DER ERRADO

### Problema: "Não consegue escanear QR Code"

**Solução:**
- [ ] Verifique se WhatsApp está atualizado
- [ ] Tente outra câmera (câmera frontal/traseira)
- [ ] Aumente o brilho da tela
- [ ] Aproxime mais o telefone

### Problema: "QR Code não aparece / erro 404"

**Solução:**
- [ ] Evolution API pode estar offline
- [ ] Execute: `python tester.py`
- [ ] Se offline, reinicie Docker: `docker-compose restart`

### Problema: "Diz que está conectado mas não envia mensagens"

**Solução:**
- [ ] Instância pode ter desconectado
- [ ] Rescaneie o QR Code
- [ ] Verifique se WhatsApp não saiu do "modo aparelho conectado"

---

## 📊 TIMELINE ESTIMADO

| Ação | Tempo |
|------|-------|
| Criar 3 instâncias | 2 minutos |
| Escanear 3 QR Codes | 10 minutos |
| Validar conexões | 1 minuto |
| **Total** | **~15 minutos** |

---

## 🚀 PRÓXIMAS ETAPAS (APÓS CONECTAR)

1. **Dashboard:**
   - http://localhost:5000
   - Login: admin@pariscred.com / Admin@2025

2. **Criar Campanha de Teste:**
   - Vá em: 📧 Campanhas
   - Clique: + Nova Campanha
   - Adicione 2 beneficiários
   - Mensagem: "Teste de disparo"
   - Clique: ⚡ DISPARAR

3. **Ver Resultado:**
   - Verifique no WhatsApp se a mensagem chegou
   - Confirme botões interativos

---

## 📞 DÚVIDAS?

Se não conseguir:
1. Envie screenshot do erro
2. Execute: `python explorador_api.py` para debug
3. Verifique logs: `python debug_endpoints.py`

---

**Você está aqui:**
```
Criar Sistema SaaS ✓
└── Autenticação ✓
└── Painel Admin ✓
└── BD Persistente ✓
└── 🔴 CONECTAR WHATSAPP ← VOCÊ ESTÁ AQUI
└── Testar Disparos
└── Deploy Produção
```

Após este passo, tudo vai funcionar! 💪
