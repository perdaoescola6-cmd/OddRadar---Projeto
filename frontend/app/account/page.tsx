'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft,
  User,
  Mail,
  Calendar,
  Shield,
  CreditCard,
  LogOut
} from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

export default function AccountPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const checkAuth = async () => {
      const supabase = createClient()
      const { data: { user: authUser } } = await supabase.auth.getUser()
      
      if (!authUser) {
        router.push('/auth/login')
        return
      }

      // Fetch subscription data
      const { data: subscription } = await supabase
        .from('subscriptions')
        .select('*')
        .eq('user_id', authUser.id)
        .maybeSingle()

      setUser({
        id: authUser.id,
        email: authUser.email,
        created_at: authUser.created_at,
        subscription: subscription ? {
          plan: subscription.plan,
          expires_at: subscription.current_period_end,
          status: subscription.status
        } : undefined
      })
    }

    checkAuth()
  }, [router])

  const handleLogout = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/auth/login')
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <header className="bg-dark-surface border-b border-dark-border p-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-400 hover:text-white">
              <ArrowLeft size={20} />
            </Link>
            <h1 className="text-xl font-semibold">Minha Conta</h1>
          </div>
          {user?.subscription && (
            <span className="badge badge-success">{user.subscription.plan}</span>
          )}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-3xl mx-auto p-6">
        {/* Profile Section */}
        <div className="bg-dark-surface border border-dark-border rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold mb-6 flex items-center">
            <User className="mr-2 text-blue-400" size={20} />
            Informações do Perfil
          </h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-dark-border">
              <div className="flex items-center">
                <Mail className="text-gray-400 mr-3" size={18} />
                <span className="text-gray-400">Email</span>
              </div>
              <span className="font-medium">{user.email}</span>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-dark-border">
              <div className="flex items-center">
                <Calendar className="text-gray-400 mr-3" size={18} />
                <span className="text-gray-400">Membro desde</span>
              </div>
              <span className="font-medium">
                {new Date(user.created_at || Date.now()).toLocaleDateString('pt-BR')}
              </span>
            </div>

            <div className="flex items-center justify-between py-3">
              <div className="flex items-center">
                <Shield className="text-gray-400 mr-3" size={18} />
                <span className="text-gray-400">Status</span>
              </div>
              <span className="text-green-400 font-medium">Ativo</span>
            </div>
          </div>
        </div>

        {/* Subscription Section */}
        <div className="bg-dark-surface border border-dark-border rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold mb-6 flex items-center">
            <CreditCard className="mr-2 text-yellow-400" size={20} />
            Assinatura
          </h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-dark-border">
              <span className="text-gray-400">Plano atual</span>
              <span className="font-medium text-yellow-400">
                {user.subscription?.plan || 'Free'}
              </span>
            </div>

            <div className="flex items-center justify-between py-3 border-b border-dark-border">
              <span className="text-gray-400">Status</span>
              <span className={`font-medium ${
                user.subscription?.status === 'active' ? 'text-green-400' : 'text-gray-400'
              }`}>
                {user.subscription?.status === 'active' ? 'Ativo' : 'Inativo'}
              </span>
            </div>

            {user.subscription?.expires_at && (
              <div className="flex items-center justify-between py-3">
                <span className="text-gray-400">Expira em</span>
                <span className="font-medium">
                  {new Date(user.subscription.expires_at).toLocaleDateString('pt-BR')}
                </span>
              </div>
            )}
          </div>

          <div className="mt-6">
            <Link href="/plans" className="btn-primary w-full text-center block">
              Gerenciar Plano
            </Link>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="bg-dark-surface border border-red-900/50 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 text-red-400">Zona de Perigo</h2>
          
          <button
            onClick={handleLogout}
            className="flex items-center justify-center w-full py-3 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-colors"
          >
            <LogOut className="mr-2" size={18} />
            Sair da Conta
          </button>
        </div>
      </main>
    </div>
  )
}
