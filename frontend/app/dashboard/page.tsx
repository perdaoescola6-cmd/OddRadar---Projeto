'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  Flame,
  ArrowLeft,
  Plus,
  X,
  Check,
  AlertCircle,
  Diamond,
  Edit3
} from 'lucide-react'

interface Bet {
  id: string
  match: {
    homeTeam: string
    awayTeam: string
  }
  market: string
  selection: string
  odds: number
  stake?: number
  note?: string
  status: 'pending' | 'won' | 'lost' | 'void' | 'manual'
  valueBet: boolean
  createdAt: string
}

const MARKETS = [
  { value: 'over_2_5', label: 'Over 2.5 Gols' },
  { value: 'under_2_5', label: 'Under 2.5 Gols' },
  { value: 'over_1_5', label: 'Over 1.5 Gols' },
  { value: 'btts_yes', label: 'Ambos Marcam - Sim' },
  { value: 'btts_no', label: 'Ambos Marcam - Não' },
  { value: '1x2_home', label: '1X2 - Vitória Casa' },
  { value: '1x2_draw', label: '1X2 - Empate' },
  { value: '1x2_away', label: '1X2 - Vitória Fora' },
]

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [bets, setBets] = useState<Bet[]>([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [showResultModal, setShowResultModal] = useState<string | null>(null)
  
  // Form state
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [market, setMarket] = useState('')
  const [odds, setOdds] = useState('')
  const [stake, setStake] = useState('')
  const [note, setNote] = useState('')

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
    
    // Load bets from localStorage
    const savedBets = localStorage.getItem('betstats_bets')
    if (savedBets) {
      setBets(JSON.parse(savedBets))
    }
  }, [router])

  // Save bets to localStorage whenever they change
  useEffect(() => {
    if (bets.length > 0) {
      localStorage.setItem('betstats_bets', JSON.stringify(bets))
    }
  }, [bets])

  // Calculate dynamic stats
  const stats = {
    total: bets.length,
    won: bets.filter(b => b.status === 'won').length,
    lost: bets.filter(b => b.status === 'lost').length,
    pending: bets.filter(b => b.status === 'pending').length,
    valueBets: bets.filter(b => b.valueBet).length,
    winRate: bets.filter(b => b.status === 'won' || b.status === 'lost').length > 0
      ? Math.round((bets.filter(b => b.status === 'won').length / bets.filter(b => b.status === 'won' || b.status === 'lost').length) * 100)
      : 0,
    streak: calculateStreak(bets)
  }

  function calculateStreak(bets: Bet[]): number {
    const resolved = bets
      .filter(b => b.status === 'won' || b.status === 'lost')
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    
    let streak = 0
    for (const bet of resolved) {
      if (bet.status === 'won') streak++
      else break
    }
    return streak
  }

  function isValueBet(odds: number, impliedProb: number = 0.5): boolean {
    const fairOdds = 1 / impliedProb
    const edge = (odds - fairOdds) / fairOdds
    return edge >= 0.05 // 5% edge
  }

  const handleAddBet = () => {
    if (!homeTeam || !awayTeam || !market || !odds) return

    const oddsNum = parseFloat(odds)
    const newBet: Bet = {
      id: Date.now().toString(),
      match: { homeTeam, awayTeam },
      market,
      selection: MARKETS.find(m => m.value === market)?.label || market,
      odds: oddsNum,
      stake: stake ? parseFloat(stake) : undefined,
      note: note || undefined,
      status: 'pending',
      valueBet: isValueBet(oddsNum),
      createdAt: new Date().toISOString()
    }

    setBets(prev => [newBet, ...prev])
    
    // Reset form
    setHomeTeam('')
    setAwayTeam('')
    setMarket('')
    setOdds('')
    setStake('')
    setNote('')
    setShowAddModal(false)
  }

  const handleUpdateResult = (betId: string, result: 'won' | 'lost' | 'void') => {
    setBets(prev => prev.map(bet => 
      bet.id === betId 
        ? { ...bet, status: result === 'won' || result === 'lost' || result === 'void' ? result : 'manual' }
        : bet
    ))
    setShowResultModal(null)
  }

  const getStatusBadge = (status: Bet['status']) => {
    switch (status) {
      case 'won': return <span className="px-2 py-1 text-xs rounded-full bg-green-500/20 text-green-400">Ganhou</span>
      case 'lost': return <span className="px-2 py-1 text-xs rounded-full bg-red-500/20 text-red-400">Perdeu</span>
      case 'void': return <span className="px-2 py-1 text-xs rounded-full bg-gray-500/20 text-gray-400">Anulada</span>
      case 'manual': return <span className="px-2 py-1 text-xs rounded-full bg-purple-500/20 text-purple-400">Manual</span>
      default: return <span className="px-2 py-1 text-xs rounded-full bg-yellow-500/20 text-yellow-400">Pendente</span>
    }
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
            <h1 className="text-xl font-semibold">Dashboard</h1>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
            >
              <Plus size={18} />
              <span>Adicionar Aposta</span>
            </button>
            {user?.subscription && (
              <span className="badge badge-success">{user.subscription.plan}</span>
            )}
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto p-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <BarChart3 className="text-blue-400" size={24} />
              <span className="text-xs text-gray-500">Total</span>
            </div>
            <p className="text-2xl font-bold">{stats.total}</p>
            <p className="text-sm text-gray-400">Apostas registradas</p>
          </div>

          <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="text-green-400" size={24} />
              <span className="text-xs text-gray-500">{stats.won}W / {stats.lost}L</span>
            </div>
            <p className="text-2xl font-bold">{stats.winRate}%</p>
            <p className="text-sm text-gray-400">Taxa de acerto</p>
          </div>

          <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <Diamond className="text-yellow-400" size={24} />
              <span className="text-xs text-gray-500">Value</span>
            </div>
            <p className="text-2xl font-bold">{stats.valueBets}</p>
            <p className="text-sm text-gray-400">Apostas com valor</p>
          </div>

          <div className="bg-dark-surface border border-dark-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <Flame className="text-orange-400" size={24} />
              <span className="text-xs text-gray-500">Streak</span>
            </div>
            <p className="text-2xl font-bold">{stats.streak}</p>
            <p className="text-sm text-gray-400">Vitórias seguidas</p>
          </div>
        </div>

        {/* Bets List */}
        <div className="bg-dark-surface border border-dark-border rounded-xl overflow-hidden">
          <div className="p-4 border-b border-dark-border flex items-center justify-between">
            <h2 className="font-semibold">Suas Apostas</h2>
            <span className="text-sm text-gray-400">{stats.pending} pendentes</span>
          </div>
          
          {bets.length === 0 ? (
            <div className="p-12 text-center">
              <Target className="mx-auto text-gray-500 mb-4" size={48} />
              <h3 className="text-lg font-semibold mb-2">Nenhuma aposta registrada</h3>
              <p className="text-gray-400 mb-6">
                Clique em "Adicionar Aposta" para começar a rastrear suas apostas.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-dark-border">
              {bets.map(bet => (
                <div key={bet.id} className="p-4 hover:bg-dark-border/30 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-1">
                        <span className="font-medium">{bet.match.homeTeam} vs {bet.match.awayTeam}</span>
                        {bet.valueBet && (
                          <span className="flex items-center space-x-1 px-2 py-0.5 text-xs rounded-full bg-yellow-500/20 text-yellow-400">
                            <Diamond size={12} />
                            <span>Value</span>
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-400">
                        <span>{bet.selection}</span>
                        <span>@{bet.odds.toFixed(2)}</span>
                        {bet.stake && <span>R${bet.stake}</span>}
                        <span>{new Date(bet.createdAt).toLocaleDateString('pt-BR')}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      {getStatusBadge(bet.status)}
                      {bet.status === 'pending' && (
                        <button
                          onClick={() => setShowResultModal(bet.id)}
                          className="p-2 text-gray-400 hover:text-white hover:bg-dark-border rounded-lg transition-colors"
                          title="Marcar resultado"
                        >
                          <Edit3 size={16} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Add Bet Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-dark-surface border border-dark-border rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Adicionar Aposta</h3>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Time Casa</label>
                  <input
                    type="text"
                    value={homeTeam}
                    onChange={(e) => setHomeTeam(e.target.value)}
                    placeholder="Ex: Chelsea"
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Time Fora</label>
                  <input
                    type="text"
                    value={awayTeam}
                    onChange={(e) => setAwayTeam(e.target.value)}
                    placeholder="Ex: Arsenal"
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Mercado</label>
                <select
                  value={market}
                  onChange={(e) => setMarket(e.target.value)}
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-blue-500 focus:outline-none"
                >
                  <option value="">Selecione...</option>
                  {MARKETS.map(m => (
                    <option key={m.value} value={m.value}>{m.label}</option>
                  ))}
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Odd</label>
                  <input
                    type="number"
                    step="0.01"
                    value={odds}
                    onChange={(e) => setOdds(e.target.value)}
                    placeholder="1.85"
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Stake (opcional)</label>
                  <input
                    type="number"
                    value={stake}
                    onChange={(e) => setStake(e.target.value)}
                    placeholder="R$ 50"
                    className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Observação (opcional)</label>
                <input
                  type="text"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Ex: Análise do BetStats"
                  className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 py-2.5 px-4 rounded-lg bg-dark-border hover:bg-gray-700 text-white font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddBet}
                disabled={!homeTeam || !awayTeam || !market || !odds}
                className="flex-1 py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium transition-colors"
              >
                Salvar Aposta
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Result Modal */}
      {showResultModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-dark-surface border border-dark-border rounded-2xl p-6 max-w-sm w-full shadow-2xl">
            <div className="text-center mb-6">
              <AlertCircle className="mx-auto text-yellow-400 mb-4" size={32} />
              <h3 className="text-lg font-semibold mb-2">Marcar resultado manualmente</h3>
              <p className="text-gray-400 text-sm">
                Não encontramos esse jogo na base de dados. Você pode marcar o resultado manualmente.
              </p>
            </div>
            
            <div className="space-y-2">
              <button
                onClick={() => handleUpdateResult(showResultModal, 'won')}
                className="w-full py-3 px-4 rounded-lg bg-green-600 hover:bg-green-700 text-white font-medium transition-colors flex items-center justify-center space-x-2"
              >
                <Check size={18} />
                <span>Ganhou</span>
              </button>
              <button
                onClick={() => handleUpdateResult(showResultModal, 'lost')}
                className="w-full py-3 px-4 rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium transition-colors flex items-center justify-center space-x-2"
              >
                <X size={18} />
                <span>Perdeu</span>
              </button>
              <button
                onClick={() => handleUpdateResult(showResultModal, 'void')}
                className="w-full py-3 px-4 rounded-lg bg-gray-600 hover:bg-gray-700 text-white font-medium transition-colors"
              >
                Anulada
              </button>
            </div>
            
            <button
              onClick={() => setShowResultModal(null)}
              className="w-full mt-4 py-2 text-gray-400 hover:text-white transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
