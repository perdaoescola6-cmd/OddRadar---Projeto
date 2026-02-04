import Stripe from 'stripe'

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2026-01-28.clover',
  typescript: true,
})

// Price IDs mapping
export const STRIPE_PRICES = {
  pro: process.env.STRIPE_PRICE_PRO!,
  elite: process.env.STRIPE_PRICE_ELITE!,
} as const

// Get price ID for a plan
export function getPriceIdForPlan(plan: 'pro' | 'elite'): string {
  return STRIPE_PRICES[plan]
}

// Get plan from price ID
export function getPlanFromPriceId(priceId: string): 'pro' | 'elite' | null {
  if (priceId === STRIPE_PRICES.pro) return 'pro'
  if (priceId === STRIPE_PRICES.elite) return 'elite'
  return null
}
