'use client'

import { useState, useEffect } from 'react'
import { MessageCircle, BarChart3, CreditCard, User, LogOut, Send, Menu, X } from 'lucide-react'
import Link from 'next/link'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface User {
  id: number
  email: string
  subscription?: {
    plan: string
    expires_at: string
    status: string
  }
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [user, setUser] = useState<User | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const quickSuggestions = [
    "Benfica x Porto",
    "Chelsea over 2.5 last 10",
    "Atlético Mineiro win rate",
    "Liverpool vs Manchester City"
  ]

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setIsAuthenticated(false)
      return
    }

    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
        setIsAuthenticated(true)
        loadChatHistory()
      } else {
        localStorage.removeItem('token')
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      setIsAuthenticated(false)
    }
  }

  const loadChatHistory = async () => {
    const token = localStorage.getItem('token')
    try {
      const response = await fetch('/api/chat/history', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const history = await response.json()
        setMessages(history.map((msg: any) => ({
          id: msg.timestamp,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        })))
      }
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    const token = localStorage.getItem('token')
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content: input })
      })

      if (response.ok) {
        const data = await response.json()
        const assistantMessage: Message = {
          id: data.timestamp,
          role: 'assistant',
          content: data.response,
          timestamp: new Date(data.timestamp)
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        const error = await response.json()
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: `❌ Erro: ${error.detail || 'Ocorreu um erro ao processar sua mensagem.'}`,
          timestamp: new Date()
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: '❌ Erro de conexão. Verifique sua internet e tente novamente.',
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setUser(null)
    setIsAuthenticated(false)
    setMessages([])
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
        <div className="card max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-accent-blue mb-2">BetStats Trader</h1>
            <p className="text-gray-400">Análise Premium de Apostas Esportivas</p>
          </div>
          
          <div className="space-y-4">
            <Link href="/auth/login" className="btn-primary w-full block text-center">
              Entrar
            </Link>
            <Link href="/auth/register" className="btn-secondary w-full block text-center">
              Criar Conta
            </Link>
          </div>
          
          <div className="mt-8 pt-6 border-t border-dark-border">
            <h3 className="text-lg font-semibold mb-4">Planos Disponíveis</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span>Plus</span>
                <span className="text-accent-green">R$30/mês</span>
              </div>
              <div className="flex justify-between">
                <span>Pro</span>
                <span className="text-accent-green">R$60/mês</span>
              </div>
              <div className="flex justify-between">
                <span>Elite</span>
                <span className="text-accent-green">R$100/mês</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-bg flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-dark-surface border-r border-dark-border transition-transform duration-300 lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between p-6 border-b border-dark-border">
          <h2 className="text-xl font-bold text-accent-blue">BetStats</h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>
        
        <nav className="p-4 space-y-2">
          <Link href="/chat" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-dark-border transition-colors">
            <MessageCircle size={20} />
            <span>Chat</span>
          </Link>
          <Link href="/dashboard" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-dark-border transition-colors">
            <BarChart3 size={20} />
            <span>Dashboard</span>
          </Link>
          <Link href="/plans" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-dark-border transition-colors">
            <CreditCard size={20} />
            <span>Planos</span>
          </Link>
          <Link href="/account" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-dark-border transition-colors">
            <User size={20} />
            <span>Conta</span>
          </Link>
        </nav>
        
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-dark-border">
          <div className="mb-4">
            <p className="text-sm text-gray-400">{user?.email}</p>
            {user?.subscription && (
              <p className="text-xs text-accent-green">
                Plano {user.subscription.plan} - {user.subscription.status}
              </p>
            )}
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-3 p-3 rounded-lg hover:bg-dark-border transition-colors w-full"
          >
            <LogOut size={20} />
            <span>Sair</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col lg:ml-0">
        {/* Header */}
        <header className="bg-dark-surface border-b border-dark-border p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-gray-400 hover:text-white"
            >
              <Menu size={24} />
            </button>
            <h1 className="text-xl font-semibold">Chat de Análises</h1>
            <div className="flex items-center space-x-2">
              {user?.subscription && (
                <span className="badge badge-success">
                  {user.subscription.plan}
                </span>
              )}
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col p-4">
          <div className="flex-1 overflow-y-auto mb-4 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <MessageCircle size={48} className="mx-auto text-gray-500 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Bem-vindo ao BetStats Chat!</h3>
                <p className="text-gray-400 mb-6">
                  Digite uma análise de jogo ou estatísticas de time para começar
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {quickSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setInput(suggestion)}
                      className="btn-secondary text-sm"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`chat-message ${message.role === 'user' ? 'chat-user' : 'chat-assistant'}`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className="text-xs opacity-70 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="chat-message chat-assistant">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-accent-blue"></div>
                  <span>Analisando...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Digite: TimeA x TimeB ou 'time over 2.5 last 10'..."
              className="input flex-1"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
