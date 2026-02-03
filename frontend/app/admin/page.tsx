'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Users, 
  Search, 
  Shield, 
  X, 
  Check, 
  RefreshCw, 
  Loader2, 
  Lock, 
  ChevronRight,
  Crown,
  Star,
  Zap,
  Calendar,
  Mail
} from 'lucide-react'
import Link from 'next/link'
import { createClient } from '@/lib/supabase/client'

interface AdminUser {
  id: string
  email: string
  name: string | null
  role: string
  created_at: string
  subscription: {
    plan: string
    status: string
    provider: string
    current_period_end: string | null
    updated_at: string
  } | null
}

const POLLING_INTERVAL = 5000

export default function AdminPanel() {
  const router = useRouter()
  const [users, setUsers] = useState<AdminUser[]>([])
  const [search, setSearch] = useState('')
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [editingPlan, setEditingPlan] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null)
  const [currentUser, setCurrentUser] = useState<any>(null)

  const supabase = createClient()

  useEffect(() => {
    checkAdminAccess()
  }, [])

  useEffect(() => {
    if (!isAuthorized) return
    
    const interval = setInterval(() => {
      loadUsers(true)
    }, POLLING_INTERVAL)
    
    return () => clearInterval(interval)
  }, [isAuthorized])

  // Subscribe to realtime changes
  useEffect(() => {
    if (!isAuthorized) return

    const channel = supabase
      .channel('admin-subscriptions')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'subscriptions',
        },
        () => {
          loadUsers(true)
        }
      )
      .subscribe()

    return () => {
      channel.unsubscribe()
    }
  }, [isAuthorized, supabase])

  const checkAdminAccess = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      
      if (!user) {
        router.push('/auth/login')
        return
      }

      setCurrentUser(user)

      const { data: profile } = await supabase
        .from('profiles')
        .select('role')
        .eq('id', user.id)
        .single()

      if (profile?.role === 'admin') {
        setIsAuthorized(true)
        loadUsers(false)
      } else {
        setIsAuthorized(false)
        setIsLoading(false)
      }
    } catch (err) {
      setIsAuthorized(false)
      setIsLoading(false)
    }
  }

  const loadUsers = async (silent: boolean = false) => {
    if (!silent) setIsLoading(true)
    else setIsRefreshing(true)
    
    try {
      const response = await fetch(`/api/admin/users?search=${search}`)

      if (response.ok) {
        const data = await response.json()
        setUsers(data)
        setError('')
      } else if (response.status === 401 || response.status === 403) {
        setIsAuthorized(false)
        setError('Acesso negado')
      } else {
        if (!silent) setError('Não foi possível carregar os usuários.')
      }
    } catch (err) {
      if (!silent) setError('Erro de conexão.')
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  const handleUpdatePlan = async (userId: string, newPlan: string) => {
    setIsSaving(true)
    setError('')
    
    try {
      const response = await fetch(`/api/admin/users/${userId}/subscription`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plan: newPlan }),
      })

      if (response.ok) {
        setSuccessMessage(`Plano atualizado para ${newPlan.toUpperCase()}`)
        setEditingPlan(null)
        loadUsers(true)
        
        // Update selected user if viewing details
        if (selectedUser?.id === userId) {
          setSelectedUser({
            ...selectedUser,
            subscription: {
              ...selectedUser.subscription!,
              plan: newPlan,
              status: 'active',
              provider: 'manual',
              updated_at: new Date().toISOString(),
            }
          })
        }
        
        setTimeout(() => setSuccessMessage(''), 3000)
      } else {
        const data = await response.json()
        setError(data.error || 'Erro ao atualizar plano')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setIsSaving(false)
    }
  }

  const getPlanIcon = (plan: string) => {
    switch (plan?.toLowerCase()) {
      case 'elite': return <Crown className="w-4 h-4 text-yellow-400" />
      case 'pro': return <Star className="w-4 h-4 text-blue-400" />
      default: return <Zap className="w-4 h-4 text-gray-400" />
    }
  }

  const getPlanBadgeClass = (plan: string) => {
    switch (plan?.toLowerCase()) {
      case 'elite': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'pro': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getStatusBadgeClass = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'trialing':
        return 'bg-green-500/20 text-green-400'
      case 'past_due':
        return 'bg-yellow-500/20 text-yellow-400'
      case 'canceled':
      case 'incomplete':
        return 'bg-red-500/20 text-red-400'
      default:
        return 'bg-gray-500/20 text-gray-400'
    }
  }

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(search.toLowerCase()) ||
    user.name?.toLowerCase().includes(search.toLowerCase())
  )

  // Not authorized view
  if (isAuthorized === false) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
        <div className="glass-card max-w-md w-full p-8 text-center">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <Lock className="text-red-400" size={32} />
          </div>
          <h1 className="text-2xl font-bold mb-2">Acesso Negado</h1>
          <p className="text-gray-400 mb-6">
            Esta área é restrita a administradores.
          </p>
          <Link
            href="/"
            className="inline-flex items-center justify-center w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors"
          >
            Voltar ao início
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Header */}
      <header className="bg-dark-surface border-b border-dark-border p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-400 hover:text-white">
              <X size={20} />
            </Link>
            <div className="flex items-center gap-2">
              <Shield className="text-blue-400" size={24} />
              <h1 className="text-xl font-semibold">Painel Admin</h1>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => loadUsers(false)}
              disabled={isLoading}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
            >
              <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
              Atualizar
            </button>
            <span className="text-sm text-gray-500">
              {currentUser?.email}
            </span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        {/* Success/Error Messages */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-500/10 border border-green-500/30 rounded-xl text-green-400 flex items-center gap-3">
            <Check size={20} />
            <span>{successMessage}</span>
          </div>
        )}
        
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 flex items-center gap-3">
            <X size={20} />
            <span>{error}</span>
            <button onClick={() => setError('')} className="ml-auto">
              <X size={16} />
            </button>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-dark-surface border border-dark-border rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Users className="text-blue-400" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">{users.length}</p>
                <p className="text-sm text-gray-400">Total Usuários</p>
              </div>
            </div>
          </div>
          <div className="bg-dark-surface border border-dark-border rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                <Crown className="text-yellow-400" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {users.filter(u => u.subscription?.plan === 'elite' && u.subscription?.status === 'active').length}
                </p>
                <p className="text-sm text-gray-400">Elite Ativos</p>
              </div>
            </div>
          </div>
          <div className="bg-dark-surface border border-dark-border rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Star className="text-blue-400" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {users.filter(u => u.subscription?.plan === 'pro' && u.subscription?.status === 'active').length}
                </p>
                <p className="text-sm text-gray-400">Pro Ativos</p>
              </div>
            </div>
          </div>
          <div className="bg-dark-surface border border-dark-border rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-500/20 rounded-lg flex items-center justify-center">
                <Zap className="text-gray-400" size={20} />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {users.filter(u => !u.subscription || u.subscription?.plan === 'free').length}
                </p>
                <p className="text-sm text-gray-400">Free</p>
              </div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por email ou nome..."
              className="w-full bg-dark-surface border border-dark-border rounded-xl pl-12 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50"
            />
          </div>
        </div>

        {/* Users List */}
        <div className="flex gap-6">
          {/* Users Table */}
          <div className="flex-1 bg-dark-surface border border-dark-border rounded-xl overflow-hidden">
            {isLoading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="animate-spin text-blue-400" size={32} />
              </div>
            ) : filteredUsers.length === 0 ? (
              <div className="text-center py-20">
                <Users className="mx-auto text-gray-500 mb-4" size={48} />
                <p className="text-gray-400">Nenhum usuário encontrado</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-dark-border/50">
                    <tr>
                      <th className="text-left px-4 py-3 text-sm font-medium text-gray-400">Usuário</th>
                      <th className="text-left px-4 py-3 text-sm font-medium text-gray-400">Plano</th>
                      <th className="text-left px-4 py-3 text-sm font-medium text-gray-400">Status</th>
                      <th className="text-left px-4 py-3 text-sm font-medium text-gray-400">Criado em</th>
                      <th className="text-right px-4 py-3 text-sm font-medium text-gray-400">Ações</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-dark-border">
                    {filteredUsers.map((user) => (
                      <tr 
                        key={user.id} 
                        className={`hover:bg-dark-border/30 cursor-pointer transition-colors ${selectedUser?.id === user.id ? 'bg-dark-border/50' : ''}`}
                        onClick={() => setSelectedUser(user)}
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center">
                              <span className="text-blue-400 text-sm font-medium">
                                {user.email[0].toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <p className="font-medium text-sm">{user.name || user.email.split('@')[0]}</p>
                              <p className="text-xs text-gray-500">{user.email}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            {getPlanIcon(user.subscription?.plan || 'free')}
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getPlanBadgeClass(user.subscription?.plan || 'free')}`}>
                              {(user.subscription?.plan || 'free').toUpperCase()}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(user.subscription?.status || 'active')}`}>
                            {user.subscription?.status || 'active'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-400">
                          {new Date(user.created_at).toLocaleDateString('pt-BR')}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <ChevronRight className="inline text-gray-500" size={16} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* User Details Panel */}
          {selectedUser && (
            <div className="w-80 bg-dark-surface border border-dark-border rounded-xl p-6 flex-shrink-0">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-semibold">Detalhes do Usuário</h3>
                <button onClick={() => setSelectedUser(null)} className="text-gray-400 hover:text-white">
                  <X size={16} />
                </button>
              </div>

              <div className="space-y-4">
                {/* User Info */}
                <div className="flex items-center gap-3 pb-4 border-b border-dark-border">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
                    <span className="text-blue-400 text-lg font-medium">
                      {selectedUser.email[0].toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium">{selectedUser.name || selectedUser.email.split('@')[0]}</p>
                    <p className="text-sm text-gray-400">{selectedUser.email}</p>
                  </div>
                </div>

                {/* Plan Editor */}
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">Plano Atual</label>
                  {editingPlan === selectedUser.id ? (
                    <div className="space-y-2">
                      <select
                        className="w-full bg-dark-border border border-dark-border rounded-lg px-3 py-2 text-white"
                        defaultValue={selectedUser.subscription?.plan || 'free'}
                        onChange={(e) => handleUpdatePlan(selectedUser.id, e.target.value)}
                        disabled={isSaving}
                      >
                        <option value="free">Free</option>
                        <option value="pro">Pro</option>
                        <option value="elite">Elite</option>
                      </select>
                      <button
                        onClick={() => setEditingPlan(null)}
                        className="text-sm text-gray-400 hover:text-white"
                      >
                        Cancelar
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getPlanIcon(selectedUser.subscription?.plan || 'free')}
                        <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getPlanBadgeClass(selectedUser.subscription?.plan || 'free')}`}>
                          {(selectedUser.subscription?.plan || 'free').toUpperCase()}
                        </span>
                      </div>
                      <button
                        onClick={() => setEditingPlan(selectedUser.id)}
                        className="text-sm text-blue-400 hover:text-blue-300"
                      >
                        Alterar
                      </button>
                    </div>
                  )}
                </div>

                {/* Status */}
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">Status</label>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(selectedUser.subscription?.status || 'active')}`}>
                    {selectedUser.subscription?.status || 'active'}
                  </span>
                </div>

                {/* Provider */}
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">Provedor</label>
                  <span className="text-white capitalize">
                    {selectedUser.subscription?.provider || 'manual'}
                  </span>
                </div>

                {/* Period End */}
                {selectedUser.subscription?.current_period_end && (
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Expira em</label>
                    <div className="flex items-center gap-2 text-white">
                      <Calendar size={16} className="text-gray-400" />
                      <span>
                        {new Date(selectedUser.subscription.current_period_end).toLocaleDateString('pt-BR')}
                      </span>
                    </div>
                  </div>
                )}

                {/* Created At */}
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">Cadastrado em</label>
                  <span className="text-white">
                    {new Date(selectedUser.created_at).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric'
                    })}
                  </span>
                </div>

                {/* Quick Actions */}
                <div className="pt-4 border-t border-dark-border space-y-2">
                  <button
                    onClick={() => handleUpdatePlan(selectedUser.id, 'elite')}
                    disabled={isSaving || selectedUser.subscription?.plan === 'elite'}
                    className="w-full py-2 rounded-lg bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    {isSaving ? <Loader2 size={16} className="animate-spin" /> : <Crown size={16} />}
                    Conceder Elite
                  </button>
                  <button
                    onClick={() => handleUpdatePlan(selectedUser.id, 'free')}
                    disabled={isSaving || selectedUser.subscription?.plan === 'free'}
                    className="w-full py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                  >
                    Revogar Assinatura
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
