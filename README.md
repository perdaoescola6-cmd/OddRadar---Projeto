# BetFaro

Plataforma premium de análise estatística para apostas esportivas com chatbot inteligente.

## 🚀 Features

- **Chatbot Inteligente**: Análise de jogos e estatísticas de times em linguagem natural
- **API-Football Integration**: Dados em tempo real de ligas e campeonatos mundiais
- **SaaS Multi-Plano**: Três níveis de assinatura (Plus, Pro, Elite)
- **Painel Admin**: Gestão completa de usuários e assinaturas
- **Dark Theme Premium**: Interface moderna e profissional
- **Autenticação Segura**: JWT com sistema de licenciamento

## 📋 Planos

- **Plus** (R$30/mês): Acesso ao chatbot, análises básicas
- **Pro** (R$60/mês): Estatísticas avançadas, mais históricos
- **Elite** (R$100/mês): Todos os recursos + Scanner de odds (em breve)

## 🛠 Tech Stack

### Backend
- **FastAPI**: Framework Python moderno
- **SQLModel**: ORM com Pydantic
- **SQLite**: Database para MVP
- **JWT**: Autenticação stateless
- **API-Football**: Dados esportivos
- **OpenAI GPT**: Parser de linguagem natural

### Frontend
- **Next.js 14**: React framework
- **Tailwind CSS**: Styling utilitário
- **TypeScript**: Type safety
- **Lucide React**: Icones

## 📁 Estrutura do Projeto

```
betfaro-trader/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── models.py            # SQLModel models
│   ├── database.py          # Database setup
│   ├── auth.py              # JWT authentication
│   ├── schemas.py           # Pydantic schemas
│   ├── chatbot.py           # Chatbot logic
│   └── football_api.py      # API-Football integration
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main chat interface
│   │   ├── auth/
│   │   │   ├── login/       # Login page
│   │   │   └── register/    # Register page
│   │   └── admin/           # Admin panel
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   └── tailwind.config.js  # Tailwind config
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Como Rodar Local

### Pré-requisitos
- Python 3.9+
- Node.js 18+
- npm ou yarn

### 1. Clonar o Projeto
```bash
git clone <repository-url>
cd betfaro-trader
```

### 2. Configurar Environment
```bash
# Copiar .env.example para .env
cp .env.example .env

# Editar .env com suas chaves
nano .env
```

Variáveis necessárias:
```env
# Backend
APISPORTS_KEY=your_api_sports_key
OPENAI_API_KEY=your_openai_key
JWT_SECRET=your_jwt_secret
ADMIN_API_KEY=your_admin_key

# URLs (opcional)
PLUS_URL=https://www.mercadopago.com.br/...
PRO_URL=https://www.mercadopago.com.br/...
ELITE_URL=https://www.mercadopago.com.br/...
```

### 3. Setup Backend
```bash
# Criar virtual environment
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (Linux/Mac)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Iniciar backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Setup Frontend
```bash
# Nova terminal (manter backend rodando)

# Instalar dependências
cd frontend
npm install

# Criar .env.local para frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_ADMIN_API_KEY=your_admin_key" >> .env.local

# Iniciar frontend
npm run dev
```

### 5. Acessar Aplicação
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Admin Panel: http://localhost:3000/admin

## 🚀 Deploy no Railway

### Backend Deploy
1. Criar novo projeto no Railway
2. Conectar repositório Git
3. Configurar environment variables no Railway
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deploy
Opção 1: Railway (mesmo projeto)
- Build Command: `cd frontend && npm install && npm run build`
- Start Command: `cd frontend && npm start`
- Output Directory: `frontend/.next`

Opção 2: Vercel (recomendado)
1. Conectar repositório ao Vercel
2. Configurar NEXT_PUBLIC_API_URL para Railway backend
3. Deploy automático

## 🔧 API Endpoints

### Autenticação
- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Informações do usuário
- `GET /api/auth/subscription` - Status da assinatura

### Chat
- `POST /api/chat` - Enviar mensagem
- `GET /api/chat/history` - Histórico de conversas

### Planos
- `GET /api/plans` - Planos disponíveis

### Admin (protegido)
- `GET /api/admin/users` - Listar usuários
- `GET /api/admin/user/{email}` - Detalhes do usuário
- `POST /api/admin/grant` - Conceder assinatura
- `POST /api/admin/revoke` - Revogar assinatura

## 💡 Como Usar

### 1. Criar Conta
- Acesse `/auth/register`
- Preencha e-mail e senha
- Faça login

### 2. Escolher Plano
- Acesse links do Mercado Pago:
  - Plus: [Link MP]
  - Pro: [Link MP]
  - Elite: [Link MP]

### 3. Ativação Manual (Admin)
- Admin concede acesso via `/admin`
- Usuário recebe acesso ao chat

### 4. Usar Chatbot
Exemplos de comandos:
```
Benfica x Porto
Chelsea over 2.5 last 10
Atlético Mineiro win rate
Liverpool away last 20 over 1.5
```

## 🔒 Segurança

- JWT tokens com expiração
- Rate limiting na API
- Admin API key protection
- Password hashing com bcrypt
- CORS configurado para produção

## 📈 TODO - Fase 2

- [ ] Webhook Mercado Pago para ativação automática
- [ ] Scanner de odds (plano Elite)
- [ ] Análises EV avançadas
- [ ] Corners/cards por fixture via API
- [ ] Sistema de notificações
- [ ] Dashboard analytics
- [ ] Mobile app (React Native)

## 🐛 Troubleshooting

### Common Issues

**Backend não inicia:**
- Verificar se Python 3.9+ está instalado
- Ativar virtual environment
- Instalar dependências com `pip install -r requirements.txt`

**Frontend errors:**
- Verificar Node.js 18+
- Limpar cache: `rm -rf .next && npm install`
- Verificar NEXT_PUBLIC_API_URL no .env.local

**API-Football errors:**
- Verificar APISPORTS_KEY válida
- Checar rate limits da API
- Monitorar logs do backend

**Chatbot não responde:**
- Verificar assinatura ativa do usuário
- Checar OPENAI_API_KEY configurada
- Verificar logs para parsing errors

## 📞 Suporte

Para suporte técnico:
1. Verificar logs no Railway/Vercel
2. Consultar documentação da API
3. Abrir issue no repositório

## 📄 Licença

Este projeto é proprietário. Todos os direitos reservados.

---

**Desenvolvido com ❤️ para a comunidade de apostadores brasileiros**
