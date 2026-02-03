'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  MessageCircle, 
  BarChart3, 
  CreditCard, 
  User, 
  LogOut, 
  Menu, 
  X, 
  HelpCircle,
  Copy,
  Check,
  ChevronRight,
  AlertTriangle,
  Zap,
  BookOpen,
  Target,
  Search
} from 'lucide-react'

export default function AjudaPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const examples = {
    basic: [
      { text: 'Arsenal x Chelsea', description: 'Formato básico com x' },
      { text: 'Benfica vs Porto', description: 'Formato com vs' },
      { text: 'Flamengo x Palmeiras', description: 'Times brasileiros' },
    ],
    markets: [
      { text: 'Benfica x Porto over 2.5', description: 'Com mercado Over 2.5' },
      { text: 'Inter x Milan btts sim', description: 'Com BTTS (ambos marcam)' },
      { text: 'Liverpool x City under 3.5', description: 'Com mercado Under 3.5' },
    ],
    complete: [
      { text: 'Chelsea x Arsenal over 2.5 btts sim @2.10', description: 'Completo com odds' },
      { text: 'Real Madrid x Barcelona o2.5 @1.85', description: 'Formato abreviado' },
    ]
  }

  const markets = [
    { name: 'Over/Under 1.5', aliases: ['o1.5', 'over 1.5', 'u1.5', 'under 1.5', 'mais de 1.5', 'menos de 1.5'] },
    { name: 'Over/Under 2.5', aliases: ['o2.5', 'over 2.5', 'u2.5', 'under 2.5', 'mais de 2.5', 'menos de 2.5'] },
    { name: 'Over/Under 3.5', aliases: ['o3.5', 'over 3.5', 'u3.5', 'under 3.5'] },
    { name: 'BTTS (Ambos Marcam)', aliases: ['btts', 'btts sim', 'btts yes', 'ambos marcam', 'btts nao', 'btts no'] },
  ]

  const errors = [
    {
      title: 'Não encontrei esse jogo com segurança',
      icon: '🔍',
      causes: [
        'Nome do time diferente do cadastro na API',
        'Jogo ainda não está listado (muito distante)',
        'Existem times com nome parecido',
      ],
      solutions: [
        'Tente escrever o nome completo (ex: "Al-Qadisiyah" em vez de abreviar)',
        'Remova hífens/acentos se necessário',
        'Aguarde o bot sugerir opções e escolha uma',
      ]
    },
    {
      title: 'Encontrei mais de um time',
      icon: '👥',
      causes: [
        'Existem times com nomes similares em diferentes países/ligas',
      ],
      solutions: [
        'Selecione a opção com país/liga correta',
        'Use o nome mais específico do time',
      ]
    },
    {
      title: 'Dados insuficientes para 10 jogos',
      icon: '📊',
      causes: [
        'O time pode ter poucos jogos oficiais recentes',
        'Time de divisão inferior ou recém-promovido',
      ],
      solutions: [
        'O bot usará os jogos disponíveis e avisará',
        'Tente outro jogo com times mais ativos',
      ]
    },
  ]

  const tips = [
    'Sempre comece com TimeA x TimeB',
    'Depois adicione mercado e odds (opcional)',
    'Não precisa de emojis nem pontuação',
    'Se o bot pedir confirmação, escolha as opções (não redigite do zero)',
    'Use "x" ou "vs" como separador entre os times',
    'Para times árabes, use o nome completo (ex: Al-Hilal)',
  ]

  return (
    <div className="h-screen bg-dark-bg flex overflow-hidden">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-dark-surface border-r border-dark-border transition-transform duration-300 lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between p-6 border-b border-dark-border">
          <h2 className="text-xl font-bold text-accent-blue">BetFaro</h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>
        
        <nav className="p-4 space-y-2">
          <Link href="/" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-dark-border transition-colors">
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
          <Link href="/ajuda" className="flex items-center space-x-3 p-3 rounded-lg bg-dark-border transition-colors">
            <HelpCircle size={20} />
            <span>Ajuda</span>
          </Link>
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="bg-dark-surface border-b border-dark-border p-4 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-gray-400 hover:text-white"
              >
                <Menu size={24} />
              </button>
              <h1 className="text-xl font-semibold flex items-center gap-2">
                <HelpCircle className="text-caramelo" size={24} />
                Central de Ajuda
              </h1>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-8">
            
            {/* Hero Section */}
            <div className="text-center mb-10">
              <h1 className="text-3xl font-bold mb-3 bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
                Como usar o BetFaro
              </h1>
              <p className="text-gray-400 text-lg">
                Guia completo para aproveitar ao máximo suas análises
              </p>
            </div>

            {/* Section 1: Como funciona */}
            <section className="bg-dark-surface border border-dark-border rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
                  <Zap className="text-caramelo" size={20} />
                </div>
                <h2 className="text-xl font-semibold">Como o bot funciona</h2>
              </div>
              
              <div className="space-y-4 text-gray-300">
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/20 text-caramelo flex items-center justify-center text-sm font-bold">1</span>
                  <p><strong>Identifica os times</strong> no texto que você digita</p>
                </div>
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/20 text-caramelo flex items-center justify-center text-sm font-bold">2</span>
                  <p><strong>Busca a partida</strong> correta na API (próximos jogos / fixtures)</p>
                </div>
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/20 text-caramelo flex items-center justify-center text-sm font-bold">3</span>
                  <div>
                    <p className="mb-2"><strong>Para análise, usa:</strong></p>
                    <ul className="ml-4 space-y-1 text-sm text-gray-400">
                      <li>• Últimos <strong className="text-white">10 jogos oficiais</strong> de cada time (20 no total)</li>
                      <li>• Exclui amistosos e jogos beneficentes</li>
                      <li>• <strong className="text-white">Forma recente</strong> mostra últimos 5 jogos (derivado dos 10 oficiais)</li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>

            {/* Section 2: Formatos aceitos */}
            <section className="bg-dark-surface border border-dark-border rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                  <BookOpen className="text-green-400" size={20} />
                </div>
                <h2 className="text-xl font-semibold">Formatos aceitos</h2>
              </div>

              {/* Basic Examples */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Básico</h3>
                <div className="grid gap-2">
                  {examples.basic.map((ex, i) => (
                    <div key={i} className="flex items-center justify-between bg-dark-bg rounded-lg p-3">
                      <div className="flex items-center gap-3">
                        <code className="bg-dark-border px-3 py-1.5 rounded-lg text-green-400 font-mono text-sm">
                          {ex.text}
                        </code>
                        <span className="text-gray-500 text-sm">{ex.description}</span>
                      </div>
                      <button
                        onClick={() => copyToClipboard(ex.text, i)}
                        className="p-2 hover:bg-dark-border rounded-lg transition-colors"
                      >
                        {copiedIndex === i ? (
                          <Check size={16} className="text-green-400" />
                        ) : (
                          <Copy size={16} className="text-gray-500" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* With Markets */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Com Mercados</h3>
                <div className="grid gap-2">
                  {examples.markets.map((ex, i) => (
                    <div key={i} className="flex items-center justify-between bg-dark-bg rounded-lg p-3">
                      <div className="flex items-center gap-3">
                        <code className="bg-dark-border px-3 py-1.5 rounded-lg text-caramelo font-mono text-sm">
                          {ex.text}
                        </code>
                        <span className="text-gray-500 text-sm">{ex.description}</span>
                      </div>
                      <button
                        onClick={() => copyToClipboard(ex.text, i + 10)}
                        className="p-2 hover:bg-dark-border rounded-lg transition-colors"
                      >
                        {copiedIndex === i + 10 ? (
                          <Check size={16} className="text-green-400" />
                        ) : (
                          <Copy size={16} className="text-gray-500" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Complete */}
              <div>
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Completo (com odds)</h3>
                <div className="grid gap-2">
                  {examples.complete.map((ex, i) => (
                    <div key={i} className="flex items-center justify-between bg-dark-bg rounded-lg p-3">
                      <div className="flex items-center gap-3">
                        <code className="bg-dark-border px-3 py-1.5 rounded-lg text-yellow-400 font-mono text-sm">
                          {ex.text}
                        </code>
                        <span className="text-gray-500 text-sm">{ex.description}</span>
                      </div>
                      <button
                        onClick={() => copyToClipboard(ex.text, i + 20)}
                        className="p-2 hover:bg-dark-border rounded-lg transition-colors"
                      >
                        {copiedIndex === i + 20 ? (
                          <Check size={16} className="text-green-400" />
                        ) : (
                          <Copy size={16} className="text-gray-500" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Section 3: Mercados suportados */}
            <section className="bg-dark-surface border border-dark-border rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
                  <Target className="text-purple-400" size={20} />
                </div>
                <h2 className="text-xl font-semibold">Mercados suportados</h2>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {markets.map((market, i) => (
                  <div key={i} className="bg-dark-bg rounded-xl p-4">
                    <h3 className="font-semibold text-white mb-2">{market.name}</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {market.aliases.map((alias, j) => (
                        <span key={j} className="text-xs bg-dark-border text-gray-400 px-2 py-1 rounded">
                          {alias}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Section 4: Erros comuns */}
            <section className="bg-dark-surface border border-dark-border rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center">
                  <AlertTriangle className="text-red-400" size={20} />
                </div>
                <h2 className="text-xl font-semibold">Erros comuns e como resolver</h2>
              </div>

              <div className="space-y-4">
                {errors.map((error, i) => (
                  <div key={i} className="bg-dark-bg rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-xl">{error.icon}</span>
                      <h3 className="font-semibold text-red-400">"{error.title}"</h3>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Possíveis causas</h4>
                        <ul className="space-y-1">
                          {error.causes.map((cause, j) => (
                            <li key={j} className="text-sm text-gray-400 flex items-start gap-2">
                              <span className="text-red-400">•</span>
                              {cause}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Como resolver</h4>
                        <ul className="space-y-1">
                          {error.solutions.map((solution, j) => (
                            <li key={j} className="text-sm text-gray-400 flex items-start gap-2">
                              <span className="text-green-400">✓</span>
                              {solution}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Section 5: Dicas rápidas */}
            <section className="bg-dark-surface border border-dark-border rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-yellow-500/20 flex items-center justify-center">
                  <Search className="text-yellow-400" size={20} />
                </div>
                <h2 className="text-xl font-semibold">Dicas rápidas para pesquisar</h2>
              </div>

              <div className="grid md:grid-cols-2 gap-3">
                {tips.map((tip, i) => (
                  <div key={i} className="flex items-center gap-3 bg-dark-bg rounded-lg p-3">
                    <div className="w-6 h-6 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center justify-center text-xs font-bold flex-shrink-0">
                      {i + 1}
                    </div>
                    <span className="text-sm text-gray-300">{tip}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* CTA Section */}
            <section className="bg-gradient-to-r from-blue-600/20 to-green-600/20 border border-blue-500/30 rounded-2xl p-8 text-center">
              <h2 className="text-2xl font-bold mb-3">Quer testar agora?</h2>
              <p className="text-gray-400 mb-6">
                Vá para o Chat e faça sua primeira análise
              </p>
              <Link 
                href="/"
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
              >
                <MessageCircle size={20} />
                Ir para o Chat
                <ChevronRight size={20} />
              </Link>
            </section>

          </div>
        </div>
      </div>
    </div>
  )
}
