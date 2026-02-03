import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'
import { createAdminClient } from '@/lib/supabase/admin'
import { stripe, getPriceIdForPlan } from '@/lib/stripe'

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient()
    
    // Get authenticated user
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    
    console.log('Checkout - Auth check:', { user: user?.id, email: user?.email, error: authError?.message })
    
    if (authError || !user) {
      console.log('Checkout - Auth failed:', authError)
      return NextResponse.json(
        { error: 'Não autorizado. Faça login para continuar.' },
        { status: 401 }
      )
    }

    // Get plan from request body
    const { plan } = await request.json()
    
    if (!plan || !['pro', 'elite'].includes(plan)) {
      return NextResponse.json(
        { error: 'Plano inválido. Escolha Pro ou Elite.' },
        { status: 400 }
      )
    }

    const priceId = getPriceIdForPlan(plan as 'pro' | 'elite')
    
    if (!priceId) {
      return NextResponse.json(
        { error: 'Configuração de preço não encontrada.' },
        { status: 500 }
      )
    }

    // Get or create Stripe customer
    const adminSupabase = createAdminClient()
    const { data: subscription } = await adminSupabase
      .from('subscriptions')
      .select('stripe_customer_id')
      .eq('user_id', user.id)
      .single()

    let customerId = subscription?.stripe_customer_id

    if (!customerId) {
      // Create new Stripe customer
      const customer = await stripe.customers.create({
        email: user.email,
        metadata: {
          user_id: user.id,
        },
      })
      customerId = customer.id

      // Save customer ID to subscription record
      await adminSupabase
        .from('subscriptions')
        .upsert({
          user_id: user.id,
          stripe_customer_id: customerId,
          plan: 'free',
          status: 'active',
          provider: 'stripe',
          updated_at: new Date().toISOString(),
        })
    }

    // Create checkout session
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      success_url: `${process.env.APP_URL}/account?success=true&plan=${plan}`,
      cancel_url: `${process.env.APP_URL}/plans?canceled=true`,
      metadata: {
        user_id: user.id,
        plan: plan,
      },
      subscription_data: {
        metadata: {
          user_id: user.id,
          plan: plan,
        },
      },
      allow_promotion_codes: true,
    })

    return NextResponse.json({ url: session.url })
  } catch (error) {
    console.error('Checkout error:', error)
    return NextResponse.json(
      { error: 'Erro ao criar sessão de pagamento. Tente novamente.' },
      { status: 500 }
    )
  }
}
