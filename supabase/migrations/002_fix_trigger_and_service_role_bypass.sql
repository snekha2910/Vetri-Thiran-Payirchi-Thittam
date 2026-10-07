-- ============================================================
-- PocketSmart AI — Fix Migration 002
-- PURPOSE: Fix the on_auth_user_created trigger that causes
--          "Database error saving new user" during signup.
--          Also add service-role bypass RLS policies so the
--          backend can write to all tables.
-- APPLY: Run this in Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

-- ── 1. Fix the trigger function with error isolation ──────────
-- The EXCEPTION block prevents trigger failures from blocking signup.
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    -- Do not block user creation if profile insert fails
    RAISE WARNING 'handle_new_user: profile insert failed for user %: %', NEW.id, SQLERRM;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- ── 2. Service-role bypass policies ──────────────────────────
-- The backend uses the service_role key which bypasses RLS by default.
-- These policies are belt-and-suspenders for extra clarity.

-- profiles: service role full access
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'profiles' AND policyname = 'Service role full access on profiles'
    ) THEN
        CREATE POLICY "Service role full access on profiles"
            ON profiles FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- plans: service role full access
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'plans' AND policyname = 'Service role full access on plans'
    ) THEN
        CREATE POLICY "Service role full access on plans"
            ON plans FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- recommendations: service role full access
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'recommendations' AND policyname = 'Service role full access on recommendations'
    ) THEN
        CREATE POLICY "Service role full access on recommendations"
            ON recommendations FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- saved_recommendations: service role full access
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'saved_recommendations' AND policyname = 'Service role full access on saved_recommendations'
    ) THEN
        CREATE POLICY "Service role full access on saved_recommendations"
            ON saved_recommendations FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- uploaded_images: service role full access
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'uploaded_images' AND policyname = 'Service role full access on uploaded_images'
    ) THEN
        CREATE POLICY "Service role full access on uploaded_images"
            ON uploaded_images FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;


-- ── 3. Verify trigger was created correctly ──────────────────
SELECT
    trigger_name,
    event_object_schema,
    event_object_table,
    action_timing,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_name = 'on_auth_user_created';
