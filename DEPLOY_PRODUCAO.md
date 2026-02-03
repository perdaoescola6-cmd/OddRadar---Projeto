# 🚀 BetFaro - Guia de Deploy em Produção

> **Domínio:** betfaro.com.br  
> **Frontend:** Vercel (Next.js)  
> **Backend:** Railway (FastAPI/Python)  
> **Banco/Auth:** Supabase  
> **Pagamentos:** Stripe  

---

## 📐 1. Arquitetura Final

| Serviço | URL | Plataforma |
|---------|-----|------------|
| **Site Principal** | https://betfaro.com.br | Vercel |
| **Site (www)** | https://www.betfaro.com.br | Vercel (redirect) |
| **API do Chat** | https://api.betfaro.com.br | Railway |
| **Banco de Dados** | Supabase PostgreSQL | Supabase |
| **Autenticação** | Supabase Auth | Supabase |
| **Pagamentos** | Stripe | Stripe |

---

## 🖥️ 2. Deploy do FRONTEND (Vercel)

### 2.1 Conectar Repositório

1. Acesse [vercel.com](https://vercel.com) e faça login
2. Clique em **"Add New Project"**
3. Importe seu repositório Git
4. **IMPORTANTE:** Configure o Root Directory como `frontend`
   - Em "Root Directory", digite: `frontend`
5. Framework Preset: **Next.js** (detectado automaticamente)
6. Clique em **Deploy**

### 2.2 Variáveis de Ambiente (Vercel)

No painel do projeto Vercel, vá em **Settings → Environment Variables** e adicione:

| Variável | Valor | Ambiente |
|----------|-------|----------|
| `NEXT_PUBLIC_APP_URL` | `https://betfaro.com.br` | Production |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://SEU_PROJETO.supabase.co` | Production |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIs...` | Production |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIs...` | Production |
| `STRIPE_SECRET_KEY` | `sk_live_...` | Production |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Production |
| `STRIPE_PRICE_PRO` | `price_...` (ID do produto Pro no Stripe) | Production |
| `STRIPE_PRICE_ELITE` | `price_...` (ID do produto Elite no Stripe) | Production |
| `BACKEND_URL` | `https://api.betfaro.com.br` | Production |
| `INTERNAL_API_KEY` | `betfaro_internal_2024` (ou gere um novo) | Production |

> ⚠️ **IMPORTANTE:** Use as chaves **LIVE** do Stripe para produção (começam com `sk_live_` e `pk_live_`)

### 2.3 Adicionar Domínio no Vercel

1. No painel do projeto, vá em **Settings → Domains**
2. Adicione: `betfaro.com.br`
3. Adicione: `www.betfaro.com.br`
4. O Vercel vai mostrar os registros DNS necessários

---

## 🐍 3. Deploy do BACKEND (Railway)

### 3.1 Criar Projeto no Railway

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha seu repositório
5. **IMPORTANTE:** Configure o Root Directory como `backend`
   - Em Settings → Root Directory: `backend`

### 3.2 Configurar Build

O Railway detectará automaticamente o Python. Verifique:
- **Builder:** Nixpacks
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3.3 Variáveis de Ambiente (Railway)

No painel do projeto Railway, vá em **Variables** e adicione:

| Variável | Valor |
|----------|-------|
| `ALLOWED_ORIGINS` | `https://betfaro.com.br,https://www.betfaro.com.br` |
| `APISPORTS_KEY` | `sua_chave_api_sports` |
| `APISPORTS_BASE_URL` | `https://v3.football.api-sports.io` |
| `OPENAI_API_KEY` | `sk-...` |
| `JWT_SECRET` | `gere_uma_chave_secreta_forte_aqui` |
| `ADMIN_API_KEY` | `sua_chave_admin_segura` |
| `INTERNAL_API_KEY` | `betfaro_internal_2024` (mesmo do Vercel) |
| `DATABASE_URL` | `sqlite:///./betfaro.db` (ou PostgreSQL se preferir) |

> 💡 **Dica:** Para gerar um JWT_SECRET seguro, use: `openssl rand -hex 32`

### 3.4 Adicionar Domínio Customizado no Railway

1. No painel do projeto, vá em **Settings → Networking → Custom Domain**
2. Adicione: `api.betfaro.com.br`
3. O Railway vai mostrar o registro CNAME necessário

---

## 🌐 4. Configuração DNS na Hostinger

Acesse o painel DNS da Hostinger para o domínio `betfaro.com.br`.

### 4.1 Registros para Vercel (Frontend)

| Tipo | Nome/Host | Valor | TTL |
|------|-----------|-------|-----|
| `A` | `@` | `76.76.21.21` | 3600 |
| `CNAME` | `www` | `cname.vercel-dns.com` | 3600 |

> ⚠️ **Nota:** O IP `76.76.21.21` é o IP padrão do Vercel. Confirme no painel do Vercel se é o mesmo.

### 4.2 Registro para Railway (Backend API)

| Tipo | Nome/Host | Valor | TTL |
|------|-----------|-------|-----|
| `CNAME` | `api` | `SEU_PROJETO.up.railway.app` | 3600 |

> ⚠️ **Nota:** Substitua `SEU_PROJETO.up.railway.app` pelo domínio que o Railway fornecer.

### 4.3 Verificação TXT (se solicitado)

O Vercel pode solicitar um registro TXT para verificação:

| Tipo | Nome/Host | Valor | TTL |
|------|-----------|-------|-----|
| `TXT` | `_vercel` | `vc-domain-verify=...` | 3600 |

---

## 💳 5. Stripe em Produção (Live Mode)

### 5.1 Ativar Live Mode

1. Acesse [dashboard.stripe.com](https://dashboard.stripe.com)
2. No canto superior direito, desative **"Test mode"**
3. Complete a verificação da conta se necessário

### 5.2 Obter Chaves Live

1. Vá em **Developers → API Keys**
2. Copie:
   - **Publishable key:** `pk_live_...`
   - **Secret key:** `sk_live_...`

### 5.3 Criar Produtos e Preços

1. Vá em **Products → Add Product**
2. Crie o produto **"BetFaro Pro"**:
   - Preço: R$ 49,00/mês (recorrente)
   - Copie o `price_id`
3. Crie o produto **"BetFaro Elite"**:
   - Preço: R$ 99,00/mês (recorrente)
   - Copie o `price_id`

### 5.4 Configurar Webhook

1. Vá em **Developers → Webhooks**
2. Clique em **"Add endpoint"**
3. Configure:
   - **URL:** `https://betfaro.com.br/api/webhooks/stripe`
   - **Eventos:**
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.paid`
     - `invoice.payment_failed`
4. Após criar, copie o **Signing secret** (`whsec_...`)
5. Adicione como `STRIPE_WEBHOOK_SECRET` no Vercel

### 5.5 Checklist de Teste Stripe

- [ ] Criar conta de teste no site
- [ ] Ir para página de planos
- [ ] Clicar em "Assinar Pro" ou "Assinar Elite"
- [ ] Completar pagamento com cartão real
- [ ] Verificar se webhook foi recebido (Stripe Dashboard → Webhooks → Logs)
- [ ] Verificar se subscription foi criada no Supabase
- [ ] Verificar se usuário tem acesso às features do plano

---

## ✅ 6. Verificações Finais

Execute esta checklist antes de considerar o deploy completo:

### 6.1 Frontend (Vercel)
- [ ] https://betfaro.com.br abre corretamente
- [ ] https://www.betfaro.com.br redireciona para betfaro.com.br
- [ ] Certificado SSL ativo (cadeado verde)
- [ ] Página de login funciona
- [ ] Página de registro funciona
- [ ] Página de planos carrega

### 6.2 Backend (Railway)
- [ ] https://api.betfaro.com.br/health retorna `{"ok": true, ...}`
- [ ] Certificado SSL ativo
- [ ] Logs sem erros no Railway Dashboard

### 6.3 Autenticação (Supabase)
- [ ] Login com email/senha funciona
- [ ] Registro de novo usuário funciona
- [ ] Sessão persiste após refresh

### 6.4 Pagamentos (Stripe)
- [ ] Checkout abre corretamente
- [ ] Pagamento é processado
- [ ] Webhook atualiza Supabase
- [ ] Usuário recebe plano correto

### 6.5 Features
- [ ] Chat funciona (chama api.betfaro.com.br)
- [ ] Picks Diários carrega para Elite
- [ ] Dashboard funciona
- [ ] Sem erros de CORS no console

---

## 🔄 7. Rollback (Em Caso de Problemas)

### 7.1 Vercel (Frontend)
1. Vá em **Deployments** no painel do projeto
2. Encontre o deploy anterior que funcionava
3. Clique nos **3 pontos** → **"Promote to Production"**

### 7.2 Railway (Backend)
1. Vá em **Deployments** no painel do projeto
2. Encontre o deploy anterior
3. Clique em **"Redeploy"**

### 7.3 Supabase (Banco de Dados)
1. Vá em **Database → Backups**
2. Selecione um backup anterior
3. Clique em **"Restore"**

> ⚠️ **IMPORTANTE:** Supabase faz backups automáticos diários. Para planos pagos, backups point-in-time estão disponíveis.

---

## 📋 8. Resumo das URLs e Variáveis

### URLs Finais
| Serviço | URL |
|---------|-----|
| Site | https://betfaro.com.br |
| Site (www) | https://www.betfaro.com.br |
| API | https://api.betfaro.com.br |
| Health Check | https://api.betfaro.com.br/health |

### Variáveis de Ambiente - Vercel (Frontend)
```env
NEXT_PUBLIC_APP_URL=https://betfaro.com.br
NEXT_PUBLIC_SUPABASE_URL=https://SEU_PROJETO.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIs...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ELITE=price_...
BACKEND_URL=https://api.betfaro.com.br
INTERNAL_API_KEY=betfaro_internal_2024
```

### Variáveis de Ambiente - Railway (Backend)
```env
ALLOWED_ORIGINS=https://betfaro.com.br,https://www.betfaro.com.br
APISPORTS_KEY=sua_chave_api_sports
APISPORTS_BASE_URL=https://v3.football.api-sports.io
OPENAI_API_KEY=sk-...
JWT_SECRET=sua_chave_jwt_secreta
ADMIN_API_KEY=sua_chave_admin
INTERNAL_API_KEY=betfaro_internal_2024
DATABASE_URL=sqlite:///./betfaro.db
```

### Registros DNS - Hostinger
```
# Frontend (Vercel)
Tipo: A      | Host: @   | Valor: 76.76.21.21           | TTL: 3600
Tipo: CNAME  | Host: www | Valor: cname.vercel-dns.com  | TTL: 3600

# Backend (Railway)
Tipo: CNAME  | Host: api | Valor: SEU_PROJETO.up.railway.app | TTL: 3600
```

---

## 🎉 Conclusão

Após seguir todos os passos:

1. ✅ Frontend rodando 24/7 no Vercel
2. ✅ Backend rodando 24/7 no Railway
3. ✅ Domínio configurado na Hostinger
4. ✅ SSL automático em todos os serviços
5. ✅ Stripe em modo Live
6. ✅ Supabase em produção

**O BetFaro está no ar!** 🚀

---

*Guia criado em: Fevereiro 2026*
*Versão: 1.0*
