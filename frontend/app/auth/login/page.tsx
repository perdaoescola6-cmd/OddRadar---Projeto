'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Eye, EyeOff, LogIn, ArrowLeft, Check, Zap, Crown, Star } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const supabase = createClient()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (signInError) {
        if (signInError.message.includes('Invalid login credentials')) {
          setError('Email ou senha incorretos')
        } else {
          setError(signInError.message)
        }
        return
      }

      if (data.user) {
        router.push('/')
        router.refresh()
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

  const plans = [
    {
      name: 'Free',
      price: 'R$0',
      period: '',
      icon: <Zap className="w-5 h-5" />,
      color: 'from-gray-500 to-gray-600',
      borderColor: 'border-gray-500/30',
      features: ['5 análises por dia', 'Estatísticas básicas', 'Ideal para testar'],
      cta: 'Começar grátis',
      popular: false,
    },
    {
      name: 'Pro',
      price: 'R$49',
      period: '/mês',
      icon: <Star className="w-5 h-5" />,
      color: 'from-caramelo to-caramelo-accent',
      borderColor: 'border-caramelo/50',
      features: ['25 análises por dia', 'Odds de valor', 'Histórico de análises', 'Estatísticas avançadas'],
      cta: 'Assinar Pro',
      popular: true,
    },
    {
      name: 'Elite',
      price: 'R$99',
      period: '/mês',
      icon: <Crown className="w-5 h-5" />,
      color: 'from-yellow-500 to-orange-500',
      borderColor: 'border-yellow-500/50',
      features: ['100 análises por dia', 'Picks diários automáticos', 'Alertas de apostas de valor', 'Dashboard premium'],
      cta: 'Assinar Elite',
      popular: false,
    },
  ]

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background */}
      <div className="football-bg"></div>
      <div className="grid-pattern"></div>
      
      {/* Floating Football Icons */}
      <div className="football-icon">⚽</div>
      <div className="football-icon">⚽</div>
      <div className="football-icon">⚽</div>
      
      {/* Animated Gradient Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      
      {/* Main Container - Two Columns on Desktop */}
      <div className="flex flex-col lg:flex-row gap-8 max-w-6xl w-full relative z-10">
        
        {/* Login Card */}
        <div className="glass-card w-full lg:w-[420px] p-8 flex-shrink-0">
          {/* Back Button */}
          <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-6">
            <ArrowLeft size={20} />
            <span>Voltar</span>
          </Link>
          
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-caramelo to-caramelo-accent mb-4 shadow-lg shadow-caramelo/30">
              <LogIn size={28} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gradient mb-2">Bem-vindo de volta!</h1>
            <p className="text-gray-400">Entre na sua conta para continuar</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 flex items-center gap-3">
              <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2 text-gray-300">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 focus:outline-none focus:border-caramelo/50 focus:ring-2 focus:ring-caramelo/20 transition-all"
                placeholder="seu@email.com"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2 text-gray-300">
                Senha
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 pr-12 text-white placeholder-gray-500 focus:outline-none focus:border-caramelo/50 focus:ring-2 focus:ring-caramelo/20 transition-all"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full py-4 px-6 rounded-xl font-semibold text-white overflow-hidden transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-caramelo to-caramelo-accent transition-all duration-300 group-hover:from-caramelo-hover group-hover:to-caramelo"></div>
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-[radial-gradient(circle_at_50%_-20%,rgba(255,255,255,0.3),transparent_70%)]"></div>
              <span className="relative flex items-center justify-center gap-2">
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Entrando...</span>
                  </>
                ) : (
                  <>
                    <LogIn size={20} />
                    <span>Entrar</span>
                  </>
                )}
              </span>
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-gray-400">
              Não tem uma conta?{' '}
              <Link href="/auth/register" className="text-caramelo hover:text-caramelo-hover font-medium transition-colors">
                Criar conta grátis
              </Link>
            </p>
          </div>
        </div>

        {/* Plans Section */}
        <div className="flex-1 hidden lg:block">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-white mb-2">🐕 Aposte como um insider com o BetFaro</h2>
            <p className="text-gray-400">Dados reais, análises profundas e as melhores oportunidades do dia.</p>
          </div>
          
          <div className="grid gap-4">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative p-5 rounded-2xl bg-white/5 border ${plan.borderColor} backdrop-blur-sm transition-all hover:bg-white/10 ${plan.popular ? 'ring-2 ring-caramelo/50' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-caramelo to-caramelo-hover text-white text-xs font-bold rounded-full">
                    MAIS POPULAR
                  </div>
                )}
                
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${plan.color} flex items-center justify-center text-white flex-shrink-0`}>
                    {plan.icon}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-baseline gap-2 mb-2">
                      <h3 className="text-lg font-bold text-white">{plan.name}</h3>
                      <span className="text-2xl font-bold text-white">{plan.price}</span>
                      <span className="text-gray-400 text-sm">{plan.period}</span>
                    </div>
                    
                    <ul className="space-y-1">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm text-gray-300">
                          <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <p className="text-center text-gray-500 text-sm mt-4">
            🔒 Pagamento seguro via Stripe
          </p>
        </div>
      </div>
    </div>
  )
}
