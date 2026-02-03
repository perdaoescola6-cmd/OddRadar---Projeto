'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Eye, EyeOff, LogIn } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('token', data.access_token)
        router.push('/')
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Erro ao fazer login')
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
      <div className="card max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-accent-blue mb-2">BetStats Trader</h1>
          <p className="text-gray-400">Faça login na sua conta</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900 border border-red-700 rounded-lg text-red-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              E-mail
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input w-full"
              placeholder="seu@email.com"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              Senha
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input w-full pr-12"
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <LogIn size={20} />
            <span>{isLoading ? 'Entrando...' : 'Entrar'}</span>
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-gray-400">
            Não tem uma conta?{' '}
            <Link href="/auth/register" className="text-accent-blue hover:underline">
              Cadastre-se
            </Link>
          </p>
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
