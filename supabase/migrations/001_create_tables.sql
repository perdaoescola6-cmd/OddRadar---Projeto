-- =====================================================
-- BetFaro SaaS - Supabase Database Schema
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. PROFILES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  name TEXT,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);

-- =====================================================
-- 2. SUBSCRIPTIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS public.subscriptions (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  plan TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'elite')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'trialing', 'past_due', 'canceled', 'incomplete')),
  provider TEXT NOT NULL DEFAULT 'manual' CHECK (provider IN ('stripe', 'manual')),
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  stripe_price_id TEXT,
  current_period_end TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON public.subscriptions(plan);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer ON public.subscriptions(stripe_customer_id);

-- =====================================================
-- 3. ANALYSIS USAGE TABLE (for tracking daily limits)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.analysis_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_analysis_usage_user_date ON public.analysis_usage(user_id, date);

-- =====================================================
-- 4. ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_usage ENABLE ROW LEVEL SECURITY;

-- PROFILES POLICIES
-- Users can read their own profile
CREATE POLICY "Users can read own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own profile (except role)
CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Admins can read all profiles
CREATE POLICY "Admins can read all profiles"
  ON public.profiles FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Admins can update all profiles
CREATE POLICY "Admins can update all profiles"
  ON public.profiles FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- SUBSCRIPTIONS POLICIES
-- Users can read their own subscription
CREATE POLICY "Users can read own subscription"
  ON public.subscriptions FOR SELECT
  USING (auth.uid() = user_id);

-- Admins can read all subscriptions
CREATE POLICY "Admins can read all subscriptions"
  ON public.subscriptions FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Admins can update all subscriptions
CREATE POLICY "Admins can update all subscriptions"
  ON public.subscriptions FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Admins can insert subscriptions
CREATE POLICY "Admins can insert subscriptions"
  ON public.subscriptions FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Service role can do everything (for webhooks)
CREATE POLICY "Service role full access profiles"
  ON public.profiles FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access subscriptions"
  ON public.subscriptions FOR ALL
  USING (auth.role() = 'service_role');

-- ANALYSIS USAGE POLICIES
-- Users can read their own usage
CREATE POLICY "Users can read own usage"
  ON public.analysis_usage FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own usage
CREATE POLICY "Users can insert own usage"
  ON public.analysis_usage FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own usage
CREATE POLICY "Users can update own usage"
  ON public.analysis_usage FOR UPDATE
  USING (auth.uid() = user_id);

-- =====================================================
-- 5. FUNCTIONS & TRIGGERS
-- =====================================================

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, name, role)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
    'user'
  );
  
  INSERT INTO public.subscriptions (user_id, plan, status, provider)
  VALUES (NEW.id, 'free', 'active', 'manual');
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on subscriptions
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
  BEFORE UPDATE ON public.subscriptions
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- =====================================================
-- 6. REALTIME
-- =====================================================

-- Enable realtime for subscriptions table
ALTER PUBLICATION supabase_realtime ADD TABLE public.subscriptions;

-- =====================================================
-- 7. HELPER FUNCTIONS
-- =====================================================

-- Function to check if user has active subscription
CREATE OR REPLACE FUNCTION public.has_active_subscription(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.subscriptions
    WHERE user_id = user_uuid
    AND status IN ('active', 'trialing')
    AND (current_period_end IS NULL OR current_period_end > NOW())
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's effective plan
CREATE OR REPLACE FUNCTION public.get_user_plan(user_uuid UUID)
RETURNS TEXT AS $$
DECLARE
  user_plan TEXT;
BEGIN
  SELECT plan INTO user_plan
  FROM public.subscriptions
  WHERE user_id = user_uuid
  AND status IN ('active', 'trialing')
  AND (current_period_end IS NULL OR current_period_end > NOW());
  
  RETURN COALESCE(user_plan, 'free');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to increment analysis usage
CREATE OR REPLACE FUNCTION public.increment_analysis_usage(user_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
  current_count INTEGER;
BEGIN
  INSERT INTO public.analysis_usage (user_id, date, count)
  VALUES (user_uuid, CURRENT_DATE, 1)
  ON CONFLICT (user_id, date)
  DO UPDATE SET count = analysis_usage.count + 1
  RETURNING count INTO current_count;
  
  RETURN current_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get today's usage count
CREATE OR REPLACE FUNCTION public.get_today_usage(user_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
  usage_count INTEGER;
BEGIN
  SELECT count INTO usage_count
  FROM public.analysis_usage
  WHERE user_id = user_uuid AND date = CURRENT_DATE;
  
  RETURN COALESCE(usage_count, 0);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
