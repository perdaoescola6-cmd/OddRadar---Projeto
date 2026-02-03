import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { createAdminClient } from '@/lib/supabase/admin'

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient()
    
    // Get authenticated user
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    
    if (authError || !user) {
      return NextResponse.json(
        { error: 'Não autorizado' },
        { status: 401 }
      )
    }

    // Check if user is admin
    const { data: profile } = await supabase
      .from('profiles')
      .select('role')
      .eq('id', user.id)
      .single()

    if (profile?.role !== 'admin') {
      return NextResponse.json(
        { error: 'Acesso negado. Apenas administradores.' },
        { status: 403 }
      )
    }

    // Get search param
    const searchParams = request.nextUrl.searchParams
    const search = searchParams.get('search') || ''

    // Use admin client to fetch all users
    const adminSupabase = createAdminClient()
    
    let query = adminSupabase
      .from('profiles')
      .select(`
        id,
        email,
        name,
        role,
        created_at,
        subscriptions (
          plan,
          status,
          provider,
          current_period_end,
          updated_at
        )
      `)
      .order('created_at', { ascending: false })

    if (search) {
      query = query.ilike('email', `%${search}%`)
    }

    const { data: users, error } = await query.limit(100)

    if (error) {
      console.error('Error fetching users:', error)
      return NextResponse.json(
        { error: 'Erro ao buscar usuários' },
        { status: 500 }
      )
    }

    // Transform data to match expected format
    const transformedUsers = users?.map(user => ({
      id: user.id,
      email: user.email,
      name: user.name,
      role: user.role,
      created_at: user.created_at,
      subscription: user.subscriptions?.[0] || null
    })) || []

    return NextResponse.json(transformedUsers)
  } catch (error) {
    console.error('Admin users error:', error)
    return NextResponse.json(
      { error: 'Erro interno do servidor' },
      { status: 500 }
    )
  }
}
