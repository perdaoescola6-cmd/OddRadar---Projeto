'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft,
  Check,
  Zap,
  Crown,
  Star,
  Loader2
} from 'lucide-react'

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: 'R$ 0',
    period: '/mês',
    description: 'Para começar a explorar',
    features: [
      '5 análises por dia',
      'Estatísticas básicas',
      'Suporte por email'
    ],
    icon: Star,
    color: 'gray'
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 'R$ 49',
    period: '/mês',
    description: 'Para apostadores sérios',
    features: [
      '25 análises por dia',
      'Estatísticas avançadas',
      'Análise de valor de odds',
      'Suporte prioritário',
      'Histórico de análises'
    ],
    icon: Zap,
    color: 'blue',
    popular: true
  },
  {
    id: 'elite',
    name: 'Elite',
    price: 'R$ 99',
    period: '/mês',
    description: 'Para profissionais',
    features: [
      '100 análises por dia',
      'Todas as estatísticas',
      'Alertas personalizados',
      'Dashboard exclusivo',
      'Suporte 24/7'
    ],
    icon: Crown,
    color: 'yellow'
  }
]

export default function PlansPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [processingPlan, setProcessingPlan] = useState<string | null>(null)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [selectedPlanName, setSelectedPlanName] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/auth/login')
      return
    }

    fetch('http://localhost:8000/api/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(() => router.push('/auth/login'))
  }, [router])

  const handleSelectPlan = async (planId: string, planName: string) => {
    if (planId === 'free') return
    
    setProcessingPlan(planId)
    setSelectedPlanName(planName)
    
    // Simulate payment processing (mock checkout)
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Update user subscription in localStorage (mock)
    const updatedUser = {
      ...user,
      subscription: {
        plan: planName,
        status: 'active',
        expires_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
      }
    }
    setUser(updatedUser)
    localStorage.setItem('user_subscription', JSON.stringify(updatedUser.subscription))
    
    setProcessingPlan(null)
    setShowSuccessModal(true)
  }

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <header className="bg-dark-surface border-b border-dark-border p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-400 hover:text-white">
              <ArrowLeft size={20} />
            </Link>
            <h1 className="text-xl font-semibold">Planos</h1>
          </div>
          {user?.subscription && (
            <span className="badge badge-success">{user.subscription.plan}</span>
          )}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto p-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Escolha seu plano</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Desbloqueie todo o potencial do BetStats Trader com análises ilimitadas e recursos exclusivos.
          </p>
        </div>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan) => {
            const Icon = plan.icon
            const isCurrentPlan = user?.subscription?.plan?.toLowerCase() === plan.name.toLowerCase()
            const isProcessing = processingPlan === plan.id
            
            return (
              <div 
                key={plan.name}
                className={`relative bg-dark-surface border rounded-2xl p-8 ${
                  plan.popular 
                    ? 'border-blue-500 ring-2 ring-blue-500/20' 
                    : 'border-dark-border'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="bg-blue-500 text-white text-xs font-semibold px-3 py-1 rounded-full">
                      Mais Popular
                    </span>
                  </div>
                )}

                <div className="text-center mb-6">
                  <Icon 
                    className={`mx-auto mb-4 ${
                      plan.color === 'blue' ? 'text-blue-400' :
                      plan.color === 'yellow' ? 'text-yellow-400' : 'text-gray-400'
                    }`} 
                    size={40} 
                  />
                  <h3 className="text-xl font-bold">{plan.name}</h3>
                  <p className="text-gray-400 text-sm">{plan.description}</p>
                </div>

                <div className="text-center mb-6">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-gray-400">{plan.period}</span>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-sm">
                      <Check className="text-green-400 mr-3 flex-shrink-0" size={16} />
                      <span className="text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleSelectPlan(plan.id, plan.name)}
                  disabled={isCurrentPlan || isProcessing || plan.id === 'free'}
                  className={`w-full py-3 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2 ${
                    isCurrentPlan
                      ? 'bg-green-600 text-white cursor-default'
                      : plan.id === 'free'
                        ? 'bg-dark-border text-gray-500 cursor-default'
                        : plan.popular
                          ? 'bg-blue-600 hover:bg-blue-700 text-white'
                          : 'bg-dark-border hover:bg-gray-700 text-white'
                  }`}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>Processando...</span>
                    </>
                  ) : isCurrentPlan ? (
                    <span>Plano Atual</span>
                  ) : plan.id === 'free' ? (
                    <span>Plano Gratuito</span>
                  ) : (
                    <span>Selecionar</span>
                  )}
                </button>
              </div>
            )
          })}
        </div>

        {/* FAQ or Info */}
        <div className="mt-16 text-center">
          <p className="text-gray-400">
            Dúvidas? Entre em contato: <span className="text-blue-400">suporte@betstats.com</span>
          </p>
        </div>
      </main>

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-dark-surface border border-dark-border rounded-2xl p-8 max-w-sm w-full shadow-2xl text-center">
            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Check className="text-green-400" size={32} />
            </div>
            <h3 className="text-xl font-bold mb-2">Pagamento Aprovado!</h3>
            <p className="text-gray-400 mb-6">
              Assinatura ativada. Aproveite todos os recursos do seu plano {selectedPlanName}.
            </p>
            <button
              onClick={() => {
                setShowSuccessModal(false)
                router.push('/')
              }}
              className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors"
            >
              Começar a usar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
