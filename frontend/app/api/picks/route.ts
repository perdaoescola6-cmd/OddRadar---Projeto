import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'
const INTERNAL_API_KEY = process.env.INTERNAL_API_KEY || 'betfaro_internal_2024'

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json(
        { detail: 'Not authenticated' },
        { status: 401 }
      )
    }

    // Check subscription
    const { data: subscription } = await supabase
      .from('subscriptions')
      .select('plan, status')
      .eq('user_id', user.id)
      .maybeSingle()

    if (!subscription || subscription.plan?.toLowerCase() !== 'elite') {
      return NextResponse.json(
        { detail: 'Picks Diários é exclusivo do plano Elite. Faça upgrade para acessar.' },
        { status: 403 }
      )
    }

    // Get query params
    const searchParams = request.nextUrl.searchParams
    const range = searchParams.get('range') || 'both'
    const refresh = searchParams.get('refresh') || 'false'

    // Forward request to internal backend endpoint
    const backendResponse = await fetch(
      `${BACKEND_URL}/api/internal/picks?range=${range}&refresh=${refresh}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Internal-Key': INTERNAL_API_KEY,
        },
      }
    )

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({}))
      return NextResponse.json(
        { detail: errorData.detail || 'Erro ao carregar picks do backend' },
        { status: backendResponse.status }
      )
    }

    const data = await backendResponse.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Error in picks API:', error)
    return NextResponse.json(
      { detail: 'Não consegui atualizar os picks agora. Tente novamente em instantes.' },
      { status: 500 }
    )
  }
}
