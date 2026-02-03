'use client'

import { useState, useEffect } from 'react'
import { Users, CreditCard, Search, Shield, X, Check, AlertCircle, RefreshCw, Loader2, Lock, ChevronRight } from 'lucide-react'
import Link from 'next/link'

interface AdminUser {
  id: number
  email: string
  created_at: string
  is_active: boolean
  subscription?: {
    plan: string
    expires_at: string
    status: string
  }
}

interface UserDetails {
  user: AdminUser
  subscriptions: Array<{
    id: number
    plan: string
    status: string
    expires_at: string
    created_at: string
  }>
  recent_chats: Array<{
    role: string
    content: string
    created_at: string
  }>
  audit_logs: Array<{
    action: string
    details: any
    created_at: string
  }>
}

const ADMIN_KEY = process.env.NEXT_PUBLIC_ADMIN_API_KEY || ''
const POLLING_INTERVAL = 5000

export default function AdminPanel() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [search, setSearch] = useState('')
  const [selectedUser, setSelectedUser] = useState<UserDetails | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [grantForm, setGrantForm] = useState({ email: '', plan: 'plus', days: 30 })
  const [showGrantModal, setShowGrantModal] = useState(false)
  const [editingPlan, setEditingPlan] = useState<{userId: number, plan: string} | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null)

  useEffect(() => {
    if (!ADMIN_KEY) {
      setIsAuthorized(false)
      setIsLoading(false)
    } else {
      setIsAuthorized(true)
      loadUsers(false)
    }
  }, [])

  useEffect(() => {
    if (!isAuthorized) return
    
    const interval = setInterval(() => {
      loadUsers(true)
    }, POLLING_INTERVAL)
    
    return () => clearInterval(interval)
  }, [isAuthorized])

  const loadUsers = async (silent: boolean = false) => {
    if (!silent) setIsLoading(true)
    else setIsRefreshing(true)
    
    try {
      const response = await fetch(`/api/admin/users?search=${search}`, {
        headers: {
          'X-Admin-Key': ADMIN_KEY
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data)
        setError('')
      } else if (response.status === 401) {
        setIsAuthorized(false)
        setError('Chave de admin inválida')
      } else {
        if (!silent) setError('Não foi possível carregar os usuários. Verifique a conexão.')
      }
    } catch (err) {
      if (!silent) setError('Erro de conexão. Verifique se o servidor está rodando.')
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  const loadUserDetails = async (email: string) => {
    try {
      const response = await fetch(`/api/admin/user/${encodeURIComponent(email)}`, {
        headers: {
          'X-Admin-Key': ADMIN_KEY
        }
      })

      if (response.ok) {
        const data = await response.json()
        setSelectedUser(data)
      } else {
        setError('Não foi possível carregar os detalhes do usuário')
      }
    } catch (err) {
      setError('Erro ao carregar detalhes do usuário')
    }
  }

  const handleUpdatePlan = async (userId: number, newPlan: string) => {
    setIsSaving(true)
    setError('')
    
    try {
      const response = await fetch(`/api/admin/users/${userId}/subscription?plan=${newPlan}&days=30`, {
        method: 'PATCH',
        headers: {
          'X-Admin-Key': ADMIN_KEY
        }
      })

      if (response.ok) {
        setSuccessMessage('Plano atualizado com sucesso!')
        setEditingPlan(null)
        loadUsers(false)
        
        if (selectedUser && selectedUser.user.id === userId) {
          loadUserDetails(selectedUser.user.email)
        }
        
        setTimeout(() => setSuccessMessage(''), 3000)
      } else {
        const data = await response.json()
        setError(data.detail || 'Erro ao atualizar plano')
      }
    } catch (err) {
      setError('Erro de conexão ao atualizar plano')
    } finally {
      setIsSaving(false)
    }
  }

  const handleGrant = async () => {
    if (!grantForm.email || !grantForm.plan || !grantForm.days) return

    setIsSaving(true)
    try {
      const response = await fetch('/api/admin/grant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Key': ADMIN_KEY
        },
        body: JSON.stringify(grantForm)
      })

      if (response.ok) {
        setShowGrantModal(false)
        setGrantForm({ email: '', plan: 'plus', days: 30 })
        setSuccessMessage('Assinatura concedida com sucesso!')
        loadUsers(false)
        setTimeout(() => setSuccessMessage(''), 3000)
      } else {
        const data = await response.json()
        setError(data.detail || 'Erro ao conceder assinatura')
      }
    } catch (err) {
      setError('Erro de conexão')
    } finally {
      setIsSaving(false)
    }
  }

  const handleRevoke = async (email: string) => {
    if (!confirm(`Revogar assinatura de ${email}?`)) return

    try {
      const response = await fetch('/api/admin/revoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Key': ADMIN_KEY
        },
        body: JSON.stringify({ email })
      })

      if (response.ok) {
        setSuccessMessage('Assinatura revogada')
        loadUsers(false)
        if (selectedUser?.user.email === email) {
          setSelectedUser(null)
        }
        setTimeout(() => setSuccessMessage(''), 3000)
      } else {
        setError('Erro ao revogar assinatura')
      }
    } catch (err) {
      setError('Erro de conexão')
    }
  }

  const getPlanBadgeColor = (plan: string) => {
    switch (plan?.toLowerCase()) {
      case 'plus': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'pro': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'elite': return 'bg-green-500/20 text-green-400 border-green-500/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  // Unauthorized state
  if (isAuthorized === false) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
        <div className="bg-dark-surface border border-dark-border rounded-2xl p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-8 h-8 text-red-400" />
          </div>
          <h1 className="text-2xl font-bold mb-2">Acesso Negado</h1>
          <p className="text-gray-400 mb-6">
            Você não tem permissão para acessar o painel de administração.
          </p>
          <Link href="/" className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-xl transition-colors">
            Voltar ao Início
            <ChevronRight size={18} />
          </Link>
        </div>
      </div>
    )
  }

  // Loading state
  if (isLoading && users.length === 0) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Carregando usuários...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <Shield className="text-blue-400" size={32} />
            <h1 className="text-3xl font-bold">Admin Panel</h1>
            {isRefreshing && (
              <RefreshCw className="w-5 h-5 text-gray-500 animate-spin" />
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => loadUsers(false)}
              className="flex items-center gap-2 px-4 py-2 bg-dark-surface border border-dark-border rounded-lg hover:bg-dark-border transition-colors"
            >
              <RefreshCw size={18} />
              Atualizar
            </button>
            <button
              onClick={() => setShowGrantModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
            >
              <CreditCard size={18} />
              Conceder Assinatura
            </button>
          </div>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-900/50 border border-green-700 rounded-lg text-green-300 flex items-center space-x-2">
            <Check size={20} />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-300 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
            <button
              onClick={() => loadUsers(false)}
              className="text-sm bg-red-800 hover:bg-red-700 px-3 py-1 rounded transition-colors"
            >
              Tentar novamente
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Users List */}
          <div className="lg:col-span-2">
            <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold flex items-center space-x-2">
                  <Users size={24} />
                  <span>Usuários ({users.length})</span>
                </h2>
                <div className="relative">
                  <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && loadUsers(false)}
                    placeholder="Buscar usuários..."
                    className="bg-dark-bg border border-dark-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Empty state */}
              {users.length === 0 && !isLoading && (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Nenhum usuário encontrado</h3>
                  <p className="text-gray-500">Tente uma busca diferente ou aguarde novos cadastros.</p>
                </div>
              )}

              {/* Users list */}
              <div className="space-y-3">
                {users.map((user) => (
                  <div
                    key={user.id}
                    className={`flex items-center justify-between p-4 bg-dark-bg rounded-lg border transition-colors cursor-pointer ${
                      selectedUser?.user.id === user.id 
                        ? 'border-blue-500' 
                        : 'border-dark-border hover:border-gray-600'
                    }`}
                    onClick={() => loadUserDetails(user.email)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 flex-wrap gap-y-1">
                        <span className="font-medium">{user.email}</span>
                        
                        {/* Plan dropdown or badge */}
                        {editingPlan?.userId === user.id ? (
                          <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                            <select
                              value={editingPlan.plan}
                              onChange={(e) => setEditingPlan({ ...editingPlan, plan: e.target.value })}
                              className="bg-dark-surface border border-dark-border rounded px-2 py-1 text-sm"
                            >
                              <option value="free">Free</option>
                              <option value="plus">Plus</option>
                              <option value="pro">Pro</option>
                              <option value="elite">Elite</option>
                            </select>
                            <button
                              onClick={() => handleUpdatePlan(user.id, editingPlan.plan)}
                              disabled={isSaving}
                              className="p-1 bg-green-600 hover:bg-green-700 rounded disabled:opacity-50"
                            >
                              {isSaving ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />}
                            </button>
                            <button
                              onClick={() => setEditingPlan(null)}
                              className="p-1 bg-gray-600 hover:bg-gray-700 rounded"
                            >
                              <X size={14} />
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setEditingPlan({ 
                                userId: user.id, 
                                plan: user.subscription?.plan || 'free' 
                              })
                            }}
                            className={`px-2 py-0.5 rounded border text-xs font-medium ${getPlanBadgeColor(user.subscription?.plan || 'free')}`}
                          >
                            {user.subscription?.plan || 'Free'}
                          </button>
                        )}
                        
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          user.is_active 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {user.is_active ? 'Ativo' : 'Inativo'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 mt-1">
                        Criado: {new Date(user.created_at).toLocaleDateString('pt-BR')}
                        {user.subscription?.expires_at && (
                          <span className="ml-4">
                            Expira: {new Date(user.subscription.expires_at).toLocaleDateString('pt-BR')}
                          </span>
                        )}
                      </div>
                    </div>
                    {user.subscription && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleRevoke(user.email)
                        }}
                        className="text-sm px-3 py-1 bg-red-600/20 text-red-400 hover:bg-red-600/30 rounded transition-colors"
                      >
                        Revogar
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* User Details */}
          <div className="lg:col-span-1">
            {selectedUser ? (
              <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold">Detalhes do Usuário</h3>
                  <button
                    onClick={() => setSelectedUser(null)}
                    className="text-gray-400 hover:text-white"
                  >
                    <X size={20} />
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Info */}
                  <div>
                    <h4 className="font-medium mb-3 text-gray-400 text-sm uppercase tracking-wider">Informações</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Email:</span>
                        <span className="font-medium">{selectedUser.user.email}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Status:</span>
                        <span className={selectedUser.user.is_active ? 'text-green-400' : 'text-red-400'}>
                          {selectedUser.user.is_active ? 'Ativo' : 'Inativo'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Criado em:</span>
                        <span>{new Date(selectedUser.user.created_at).toLocaleDateString('pt-BR')}</span>
                      </div>
                    </div>
                  </div>

                  {/* Subscriptions */}
                  <div>
                    <h4 className="font-medium mb-3 text-gray-400 text-sm uppercase tracking-wider">Assinaturas</h4>
                    {selectedUser.subscriptions.length === 0 ? (
                      <p className="text-gray-500 text-sm">Nenhuma assinatura</p>
                    ) : (
                      <div className="space-y-2">
                        {selectedUser.subscriptions.map((sub) => (
                          <div key={sub.id} className="p-3 bg-dark-bg rounded-lg border border-dark-border">
                            <div className="flex items-center justify-between">
                              <span className={`px-2 py-0.5 rounded border text-xs font-medium ${getPlanBadgeColor(sub.plan)}`}>
                                {sub.plan}
                              </span>
                              <span className={`text-xs ${sub.status === 'active' ? 'text-green-400' : 'text-red-400'}`}>
                                {sub.status}
                              </span>
                            </div>
                            <div className="text-xs text-gray-500 mt-2">
                              <div>Criado: {new Date(sub.created_at).toLocaleDateString('pt-BR')}</div>
                              {sub.expires_at && (
                                <div>Expira: {new Date(sub.expires_at).toLocaleDateString('pt-BR')}</div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Activity */}
                  <div>
                    <h4 className="font-medium mb-3 text-gray-400 text-sm uppercase tracking-wider">Atividade Recente</h4>
                    {selectedUser.audit_logs.length === 0 ? (
                      <p className="text-gray-500 text-sm">Nenhuma atividade</p>
                    ) : (
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {selectedUser.audit_logs.map((log, index) => (
                          <div key={index} className="text-sm p-2 bg-dark-bg rounded">
                            <div className="font-medium text-gray-300">{log.action}</div>
                            <div className="text-xs text-gray-500">
                              {new Date(log.created_at).toLocaleString('pt-BR')}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
                <div className="text-center py-8 text-gray-400">
                  <Users size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Selecione um usuário para ver detalhes</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Grant Modal */}
      {showGrantModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-dark-surface border border-dark-border rounded-xl p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">Conceder Assinatura</h3>
              <button
                onClick={() => setShowGrantModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-400">Email</label>
                <input
                  type="email"
                  value={grantForm.email}
                  onChange={(e) => setGrantForm({ ...grantForm, email: e.target.value })}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                  placeholder="usuario@exemplo.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-400">Plano</label>
                <select
                  value={grantForm.plan}
                  onChange={(e) => setGrantForm({ ...grantForm, plan: e.target.value })}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                >
                  <option value="plus">Plus</option>
                  <option value="pro">Pro</option>
                  <option value="elite">Elite</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-400">Dias</label>
                <input
                  type="number"
                  value={grantForm.days}
                  onChange={(e) => setGrantForm({ ...grantForm, days: parseInt(e.target.value) || 30 })}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
                  min="1"
                  max="365"
                />
              </div>

              <div className="flex space-x-3 pt-2">
                <button
                  onClick={handleGrant}
                  disabled={isSaving || !grantForm.email}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {isSaving ? <Loader2 size={18} className="animate-spin" /> : <Check size={18} />}
                  Conceder
                </button>
                <button
                  onClick={() => setShowGrantModal(false)}
                  className="flex-1 bg-dark-border hover:bg-gray-700 py-2 rounded-lg font-medium transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
