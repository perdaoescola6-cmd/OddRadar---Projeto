# 💳 BetFaro - Guia de Configuração de Pagamentos

Este guia explica como configurar o sistema de pagamentos do BetFaro usando **Stripe** e **Supabase**.

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração do Stripe](#configuração-do-stripe)
3. [Configuração do Supabase](#configuração-do-supabase)
4. [Variáveis de Ambiente](#variáveis-de-ambiente)
5. [Testando Localmente](#testando-localmente)
6. [Fluxo de Pagamento](#fluxo-de-pagamento)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

- Conta no [Stripe](https://stripe.com)
- Conta no [Supabase](https://supabase.com)
- Node.js 18+
- Stripe CLI (para testes locais)

---

## 💳 Configuração do Stripe

### 1. Criar Produtos e Preços

1. Acesse o [Dashboard do Stripe](https://dashboard.stripe.com)
2. Vá em **Products** > **Add product**
3. Crie dois produtos:

#### Produto Pro
- **Nome:** BetFaro Pro
- **Descrição:** 25 análises por dia, estatísticas avançadas
- **Preço:** R$49,00/mês (recorrente)
- **Copie o Price ID:** `price_xxxxxxxxxxxxx`

#### Produto Elite
- **Nome:** BetFaro Elite
- **Descrição:** 100 análises por dia, picks diários, alertas
- **Preço:** R$99,00/mês (recorrente)
- **Copie o Price ID:** `price_xxxxxxxxxxxxx`

### 2. Configurar Webhook

1. Vá em **Developers** > **Webhooks**
2. Clique em **Add endpoint**
3. Configure:
   - **URL:** `https://seu-dominio.com/api/webhooks/stripe`
   - **Eventos a escutar:**
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.paid`
     - `invoice.payment_failed`
4. Copie o **Webhook Secret:** `whsec_xxxxxxxxxxxxx`

### 3. Obter Chaves de API

1. Vá em **Developers** > **API keys**
2. Copie:
   - **Secret key:** `sk_live_xxxxxxxxxxxxx` (ou `sk_test_` para testes)
   - **Publishable key:** `pk_live_xxxxxxxxxxxxx` (ou `pk_test_` para testes)

---

## 🗄️ Configuração do Supabase

### 1. Criar Projeto

1. Acesse [Supabase Dashboard](https://app.supabase.com)
2. Crie um novo projeto
3. Anote as credenciais:
   - **Project URL:** `https://xxxxx.supabase.co`
   - **Anon Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **Service Role Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 2. Executar Migrations

1. Vá em **SQL Editor**
2. Cole e execute o conteúdo de `supabase/migrations/001_create_tables.sql`

### 3. Habilitar Realtime

1. Vá em **Database** > **Replication**
2. Habilite realtime para a tabela `subscriptions`

### 4. Configurar Auth

1. Vá em **Authentication** > **Providers**
2. Habilite **Email** provider
3. Configure URLs de redirect se necessário

---

## 🔐 Variáveis de Ambiente

### Frontend (`frontend/.env.local`)

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Stripe
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
STRIPE_PRICE_PRO=price_xxxxxxxxxxxxx
STRIPE_PRICE_ELITE=price_xxxxxxxxxxxxx

# App
APP_URL=http://localhost:3000
```

### Backend (`.env`)

```env
# Supabase (se usar no backend Python)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🧪 Testando Localmente

### 1. Instalar Stripe CLI

```bash
# Windows (Scoop)
scoop install stripe

# macOS (Homebrew)
brew install stripe/stripe-cli/stripe

# Linux
# Baixe de https://stripe.com/docs/stripe-cli
```

### 2. Login no Stripe CLI

```bash
stripe login
```

### 3. Encaminhar Webhooks para Localhost

```bash
stripe listen --forward-to localhost:3000/api/webhooks/stripe
```

Copie o webhook secret exibido e use em `STRIPE_WEBHOOK_SECRET`.

### 4. Testar Checkout

1. Acesse `http://localhost:3000/plans`
2. Clique em "Assinar Pro" ou "Assinar Elite"
3. Use cartão de teste: `4242 4242 4242 4242`
4. Data: qualquer data futura
5. CVC: qualquer 3 dígitos

### 5. Cartões de Teste

| Cenário | Número do Cartão |
|---------|------------------|
| Sucesso | 4242 4242 4242 4242 |
| Requer autenticação | 4000 0025 0000 3155 |
| Pagamento recusado | 4000 0000 0000 9995 |
| Fundos insuficientes | 4000 0000 0000 9995 |

---

## 🔄 Fluxo de Pagamento

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Usuário   │────▶│   Frontend  │────▶│  /checkout  │
│  clica em   │     │   /plans    │     │   API       │
│  "Assinar"  │     │             │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Stripe    │
                                        │  Checkout   │
                                        │   Session   │
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
             ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
             │   Sucesso   │           │  Cancelado  │           │   Webhook   │
             │  /plans?    │           │  /plans?    │           │   Stripe    │
             │  success=   │           │  canceled=  │           │             │
             │  true       │           │  true       │           │             │
             └─────────────┘           └─────────────┘           └──────┬──────┘
                                                                        │
                                                                        ▼
                                                                 ┌─────────────┐
                                                                 │  Supabase   │
                                                                 │  Atualiza   │
                                                                 │ subscription│
                                                                 └──────┬──────┘
                                                                        │
                                                                        ▼
                                                                 ┌─────────────┐
                                                                 │  Realtime   │
                                                                 │  Atualiza   │
                                                                 │  Frontend   │
                                                                 └─────────────┘
```

---

## 🔍 Verificando no Supabase

### Verificar Assinatura de um Usuário

```sql
SELECT 
  p.email,
  s.plan,
  s.status,
  s.current_period_end,
  s.provider
FROM profiles p
JOIN subscriptions s ON p.id = s.user_id
WHERE p.email = 'usuario@email.com';
```

### Listar Todas as Assinaturas Ativas

```sql
SELECT 
  p.email,
  s.plan,
  s.status,
  s.current_period_end
FROM subscriptions s
JOIN profiles p ON s.user_id = p.id
WHERE s.status IN ('active', 'trialing')
ORDER BY s.updated_at DESC;
```

### Atualizar Plano Manualmente (Admin)

```sql
UPDATE subscriptions
SET 
  plan = 'elite',
  status = 'active',
  provider = 'manual',
  updated_at = NOW()
WHERE user_id = 'uuid-do-usuario';
```

---

## 🛠️ Troubleshooting

### Webhook não está sendo recebido

1. Verifique se o Stripe CLI está rodando: `stripe listen --forward-to localhost:3000/api/webhooks/stripe`
2. Verifique se o `STRIPE_WEBHOOK_SECRET` está correto
3. Verifique os logs do Stripe CLI

### Assinatura não atualiza em tempo real

1. Verifique se o Realtime está habilitado no Supabase
2. Verifique se a tabela `subscriptions` está na publicação `supabase_realtime`
3. Verifique os logs do console do navegador

### Erro "Could not validate credentials"

1. Verifique se o token JWT está sendo enviado corretamente
2. Verifique se o usuário existe no Supabase Auth
3. Verifique as políticas RLS

### Checkout redireciona para página de erro

1. Verifique se os Price IDs estão corretos
2. Verifique se o `APP_URL` está configurado
3. Verifique os logs do servidor

---

## 📞 Suporte

- **Email:** suporte@betfaro.com
- **Docs Stripe:** https://stripe.com/docs
- **Docs Supabase:** https://supabase.com/docs

---

## ✅ Checklist de Deploy

- [ ] Criar produtos no Stripe (modo live)
- [ ] Configurar webhook no Stripe (URL de produção)
- [ ] Configurar variáveis de ambiente em produção
- [ ] Testar fluxo completo de checkout
- [ ] Testar webhook em produção
- [ ] Verificar RLS no Supabase
- [ ] Habilitar Realtime em produção
