-- Hasselize Profile Auto-Creation Trigger
-- This trigger automatically creates a profile when a new user signs up via OAuth

-- ============================================================================
-- Function: Handle new user signup
-- ============================================================================

-- Function to create profile on new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
    new_user_id UUID;
BEGIN
    new_user_id := NEW.id;

    -- Insert profile with default values
    INSERT INTO public.profiles (
        id,
        email,
        full_name,
        avatar_url,
        subscription_tier,
        credits_remaining
    )
    VALUES (
        new_user_id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
        NEW.raw_user_meta_data->>'avatar_url',
        'free',
        10  -- Start with 10 free credits
    )
    ON CONFLICT (id) DO NOTHING;  -- Handle race conditions

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- Trigger: Create profile on user signup
-- ============================================================================

-- Drop trigger if exists (for idempotency)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger to fire after new user insert
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- Grant permissions
-- ============================================================================

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO authenticated;

-- Grant anon users permission (for signup flow)
GRANT EXECUTE ON FUNCTION public.handle_new_user() TO anon;
