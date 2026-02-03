'use client'

import { useState, useEffect } from 'react'
import { Users, CreditCard, Search, Shield, X, Check, AlertCircle } from 'lucide-react'

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

export default function AdminPanel() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [search, setSearch] = useState('')
  const [selectedUser, setSelectedUser] = useState<UserDetails | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [grantForm, setGrantForm] = useState({ email: '', plan: 'plus', days: 30 })
  const [showGrantModal, setShowGrantModal] = useState(false)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`/api/admin/users?search=${search}`, {
        headers: {
          'X-Admin-Key': process.env.NEXT_PUBLIC_ADMIN_API_KEY || ''
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data)
      } else {
        setError('Failed to load users')
      }
    } catch (error) {
      setError('Error loading users')
    } finally {
      setIsLoading(false)
    }
  }

  const loadUserDetails = async (email: string) => {
    try {
      const response = await fetch(`/api/admin/user/${encodeURIComponent(email)}`, {
        headers: {
          'X-Admin-Key': process.env.NEXT_PUBLIC_ADMIN_API_KEY || ''
        }
      })

      if (response.ok) {
        const data = await response.json()
        setSelectedUser(data)
      } else {
        setError('Failed to load user details')
      }
    } catch (error) {
      setError('Error loading user details')
    }
  }

  const handleGrant = async () => {
    if (!grantForm.email || !grantForm.plan || !grantForm.days) return

    try {
      const response = await fetch('/api/admin/grant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Key': process.env.NEXT_PUBLIC_ADMIN_API_KEY || ''
        },
        body: JSON.stringify(grantForm)
      })

      if (response.ok) {
        setShowGrantModal(false)
        setGrantForm({ email: '', plan: 'plus', days: 30 })
        loadUsers()
      } else {
        setError('Failed to grant subscription')
      }
    } catch (error) {
      setError('Error granting subscription')
    }
  }

  const handleRevoke = async (email: string) => {
    if (!confirm(`Revoke subscription for ${email}?`)) return

    try {
      const response = await fetch('/api/admin/revoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Key': process.env.NEXT_PUBLIC_ADMIN_API_KEY || ''
        },
        body: JSON.stringify({ email })
      })

      if (response.ok) {
        loadUsers()
        if (selectedUser?.user.email === email) {
          setSelectedUser(null)
        }
      } else {
        setError('Failed to revoke subscription')
      }
    } catch (error) {
      setError('Error revoking subscription')
    }
  }

  const getPlanBadgeColor = (plan: string) => {
    switch (plan) {
      case 'plus': return 'badge-info'
      case 'pro': return 'badge-warning'
      case 'elite': return 'badge-success'
      default: return 'badge-danger'
    }
  }

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <Shield className="text-accent-blue" size={32} />
            <h1 className="text-3xl font-bold">Admin Panel</h1>
          </div>
          <button
            onClick={() => setShowGrantModal(true)}
            className="btn-success flex items-center space-x-2"
          >
            <CreditCard size={20} />
            <span>Grant Subscription</span>
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900 border border-red-700 rounded-lg text-red-300 flex items-center space-x-2">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Users List */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold flex items-center space-x-2">
                  <Users size={24} />
                  <span>Users</span>
                </h2>
                <div className="relative">
                  <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && loadUsers()}
                    placeholder="Search users..."
                    className="input pl-10"
                  />
                </div>
              </div>

              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-blue mx-auto"></div>
                </div>
              ) : (
                <div className="space-y-3">
                  {users.map((user) => (
                    <div
                      key={user.id}
                      className="flex items-center justify-between p-4 bg-dark-bg rounded-lg border border-dark-border hover:border-accent-blue transition-colors cursor-pointer"
                      onClick={() => loadUserDetails(user.email)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <span className="font-medium">{user.email}</span>
                          {user.subscription && (
                            <span className={`badge ${getPlanBadgeColor(user.subscription.plan)}`}>
                              {user.subscription.plan}
                            </span>
                          )}
                          {user.is_active ? (
                            <span className="badge badge-success">Active</span>
                          ) : (
                            <span className="badge badge-danger">Inactive</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-400 mt-1">
                          Created: {new Date(user.created_at).toLocaleDateString()}
                          {user.subscription && (
                            <span className="ml-4">
                              Expires: {new Date(user.subscription.expires_at).toLocaleDateString()}
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
                          className="btn-secondary text-sm"
                        >
                          Revoke
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* User Details */}
          <div className="lg:col-span-1">
            {selectedUser ? (
              <div className="card">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold">User Details</h3>
                  <button
                    onClick={() => setSelectedUser(null)}
                    className="text-gray-400 hover:text-white"
                  >
                    <X size={20} />
                  </button>
                </div>

                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium mb-2">Information</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Email:</span>
                        <span>{selectedUser.user.email}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Status:</span>
                        <span className={selectedUser.user.is_active ? 'text-green-400' : 'text-red-400'}>
                          {selectedUser.user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Created:</span>
                        <span>{new Date(selectedUser.user.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Subscriptions</h4>
                    <div className="space-y-2">
                      {selectedUser.subscriptions.map((sub) => (
                        <div key={sub.id} className="p-3 bg-dark-bg rounded border border-dark-border">
                          <div className="flex items-center justify-between">
                            <span className={`badge ${getPlanBadgeColor(sub.plan)}`}>
                              {sub.plan}
                            </span>
                            <span className={`badge ${sub.status === 'active' ? 'badge-success' : 'badge-danger'}`}>
                              {sub.status}
                            </span>
                          </div>
                          <div className="text-xs text-gray-400 mt-2">
                            Created: {new Date(sub.created_at).toLocaleDateString()}
                            {sub.expires_at && (
                              <div>
                                Expires: {new Date(sub.expires_at).toLocaleDateString()}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Recent Activity</h4>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {selectedUser.audit_logs.map((log, index) => (
                        <div key={index} className="text-sm p-2 bg-dark-bg rounded">
                          <div className="font-medium">{log.action}</div>
                          <div className="text-xs text-gray-400">
                            {new Date(log.created_at).toLocaleString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="card">
                <div className="text-center py-8 text-gray-400">
                  <Users size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Select a user to view details</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Grant Modal */}
      {showGrantModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="card max-w-md w-full">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">Grant Subscription</h3>
              <button
                onClick={() => setShowGrantModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  value={grantForm.email}
                  onChange={(e) => setGrantForm({ ...grantForm, email: e.target.value })}
                  className="input w-full"
                  placeholder="user@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Plan</label>
                <select
                  value={grantForm.plan}
                  onChange={(e) => setGrantForm({ ...grantForm, plan: e.target.value })}
                  className="input w-full"
                >
                  <option value="plus">Plus</option>
                  <option value="pro">Pro</option>
                  <option value="elite">Elite</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Days</label>
                <input
                  type="number"
                  value={grantForm.days}
                  onChange={(e) => setGrantForm({ ...grantForm, days: parseInt(e.target.value) || 30 })}
                  className="input w-full"
                  min="1"
                  max="365"
                />
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={handleGrant}
                  className="btn-success flex-1"
                >
                  Grant
                </button>
                <button
                  onClick={() => setShowGrantModal(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
