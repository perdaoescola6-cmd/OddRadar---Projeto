export type UserRole = 'user' | 'admin'

export type SubscriptionPlan = 'free' | 'pro' | 'elite'

export type SubscriptionStatus = 'active' | 'trialing' | 'past_due' | 'canceled' | 'incomplete'

export type SubscriptionProvider = 'stripe' | 'manual'

export interface Profile {
  id: string
  email: string
  name: string | null
  role: UserRole
  created_at: string
}

export interface Subscription {
  user_id: string
  plan: SubscriptionPlan
  status: SubscriptionStatus
  provider: SubscriptionProvider
  stripe_customer_id: string | null
  stripe_subscription_id: string | null
  stripe_price_id: string | null
  current_period_end: string | null
  updated_at: string
}

export interface UserWithSubscription extends Profile {
  subscription: Subscription | null
}

// Plan limits
export const PLAN_LIMITS: Record<SubscriptionPlan, number> = {
  free: 5,
  pro: 25,
  elite: 100
}

// Plan features
export const PLAN_FEATURES: Record<SubscriptionPlan, string[]> = {
  free: [
    '5 análises por dia',
    'Estatísticas básicas',
    'Ideal para testar'
  ],
  pro: [
    '25 análises por dia',
    'Odds de valor',
    'Histórico de análises',
    'Estatísticas avançadas'
  ],
  elite: [
    '100 análises por dia',
    'Picks diários automáticos',
    'Alertas de apostas de valor',
    'Dashboard premium'
  ]
}

// Plan prices
export const PLAN_PRICES: Record<SubscriptionPlan, number> = {
  free: 0,
  pro: 49,
  elite: 99
}

// Check if subscription is active
export function isSubscriptionActive(status: SubscriptionStatus | undefined): boolean {
  return status === 'active' || status === 'trialing'
}

// Get effective plan (returns 'free' if subscription is not active)
export function getEffectivePlan(subscription: Subscription | null): SubscriptionPlan {
  if (!subscription) return 'free'
  if (!isSubscriptionActive(subscription.status)) return 'free'
  return subscription.plan
}

// Check if user has access to a feature
export function hasFeatureAccess(
  subscription: Subscription | null,
  requiredPlan: SubscriptionPlan
): boolean {
  const effectivePlan = getEffectivePlan(subscription)
  const planHierarchy: SubscriptionPlan[] = ['free', 'pro', 'elite']
  return planHierarchy.indexOf(effectivePlan) >= planHierarchy.indexOf(requiredPlan)
}
