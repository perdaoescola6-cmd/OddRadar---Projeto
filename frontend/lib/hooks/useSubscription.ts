'use client'

import { useEffect, useState, useCallback } from 'react'
import { createClient } from '@/lib/supabase/client'
import { 
  Subscription, 
  Profile, 
  getEffectivePlan, 
  hasFeatureAccess, 
  PLAN_LIMITS,
  SubscriptionPlan 
} from '@/lib/supabase/types'

interface UseSubscriptionReturn {
  subscription: Subscription | null
  profile: Profile | null
  isLoading: boolean
  error: Error | null
  effectivePlan: SubscriptionPlan
  dailyLimit: number
  canAccessFeature: (requiredPlan: SubscriptionPlan) => boolean
  refetch: () => Promise<void>
}

export function useSubscription(): UseSubscriptionReturn {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const supabase = createClient()

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const { data: { user } } = await supabase.auth.getUser()
      
      if (!user) {
        setSubscription(null)
        setProfile(null)
        return
      }

      // Fetch profile
      const { data: profileData, error: profileError } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single()

      if (profileError && profileError.code !== 'PGRST116') {
        throw profileError
      }

      setProfile(profileData)

      // Fetch subscription
      const { data: subscriptionData, error: subscriptionError } = await supabase
        .from('subscriptions')
        .select('*')
        .eq('user_id', user.id)
        .single()

      if (subscriptionError && subscriptionError.code !== 'PGRST116') {
        throw subscriptionError
      }

      setSubscription(subscriptionData)
    } catch (err) {
      setError(err as Error)
      console.error('Error fetching subscription:', err)
    } finally {
      setIsLoading(false)
    }
  }, [supabase])

  useEffect(() => {
    fetchData()

    // Subscribe to realtime changes on subscriptions table
    const channel = supabase
      .channel('subscription-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'subscriptions',
        },
        (payload) => {
          console.log('Subscription changed:', payload)
          if (payload.new) {
            setSubscription(payload.new as Subscription)
          }
        }
      )
      .subscribe()

    // Subscribe to auth changes
    const { data: { subscription: authSubscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
          fetchData()
        } else if (event === 'SIGNED_OUT') {
          setSubscription(null)
          setProfile(null)
        }
      }
    )

    return () => {
      channel.unsubscribe()
      authSubscription.unsubscribe()
    }
  }, [fetchData, supabase])

  const effectivePlan = getEffectivePlan(subscription)
  const dailyLimit = PLAN_LIMITS[effectivePlan]

  const canAccessFeature = useCallback(
    (requiredPlan: SubscriptionPlan) => hasFeatureAccess(subscription, requiredPlan),
    [subscription]
  )

  return {
    subscription,
    profile,
    isLoading,
    error,
    effectivePlan,
    dailyLimit,
    canAccessFeature,
    refetch: fetchData,
  }
}
