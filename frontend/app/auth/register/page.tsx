'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Eye, EyeOff, UserPlus, ArrowLeft, Check } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const router = useRouter()
  const supabase = createClient()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    if (password !== confirmPassword) {
      setError('As senhas não coincidem')
      setIsLoading(false)
      return
    }

    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres')
      setIsLoading(false)
      return
    }

    try {
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      })

      if (signUpError) {
        if (signUpError.message.includes('already registered')) {
          setError('Este email já está cadastrado')
        } else {
          setError(signUpError.message)
        }
        return
      }

      if (data.user) {
        setSuccess(true)
        // Auto login after signup
        setTimeout(() => {
          router.push('/')
        }, 2000)
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

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
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      
      {/* Main Card */}
      <div className="glass-card max-w-md w-full p-8 relative z-10">
        {/* Back Button */}
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-6">
          <ArrowLeft size={20} />
          <span>Voltar</span>
        </Link>
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-caramelo to-caramelo-accent mb-4 shadow-lg shadow-caramelo/30">
            <UserPlus size={28} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gradient mb-2">Criar Conta</h1>
          <p className="text-gray-400">Comece sua jornada de análises premium</p>
        </div>

        {success && (
          <div className="mb-6 p-4 bg-green-500/10 border border-green-500/30 rounded-xl text-green-400 flex items-center gap-3">
            <Check className="w-5 h-5 flex-shrink-0" />
            <span>Conta criada com sucesso! Redirecionando...</span>
          </div>
        )}

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
                minLength={6}
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

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2 text-gray-300">
              Confirmar Senha
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 focus:outline-none focus:border-caramelo/50 focus:ring-2 focus:ring-caramelo/20 transition-all"
              placeholder="••••••••"
              required
              minLength={6}
            />
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
                  <span>Criando conta...</span>
                </>
              ) : (
                <>
                  <UserPlus size={20} />
                  <span>Criar Conta Grátis</span>
                </>
              )}
            </span>
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-gray-400">
            Já tem uma conta?{' '}
            <Link href="/auth/login" className="text-caramelo hover:text-caramelo-hover font-medium transition-colors">
              Faça login
            </Link>
          </p>
        </div>

        {/* Benefits */}
        <div className="mt-8 pt-6 border-t border-white/10">
          <h3 className="text-sm font-semibold mb-4 text-gray-300">O que você ganha:</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center">
                <Check size={12} className="text-green-400" />
              </div>
              <span>Análises estatísticas premium</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center">
                <Check size={12} className="text-green-400" />
              </div>
              <span>Chatbot inteligente 24/7</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <div className="w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center">
                <Check size={12} className="text-green-400" />
              </div>
              <span>Dados de +100 ligas mundiais</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
