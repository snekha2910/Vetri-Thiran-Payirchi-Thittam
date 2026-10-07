-- ============================================================
-- PocketSmart AI — Initial Database Schema
-- Run this against your Supabase PostgreSQL project.
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- TABLE: profiles
-- One row per authenticated Supabase user.
-- ============================================================
CREATE TABLE IF NOT EXISTS profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name   TEXT NOT NULL DEFAULT '',
    avatar_url  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- TABLE: plans
-- One plan per planner session (home / party / jewelry).
-- ============================================================
CREATE TABLE IF NOT EXISTS plans (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    planner_type    TEXT NOT NULL CHECK (planner_type IN ('home', 'party', 'jewelry')),
    title           TEXT NOT NULL DEFAULT '',
    budget          NUMERIC(15, 2) NOT NULL DEFAULT 0,
    estimated_cost  NUMERIC(15, 2) NOT NULL DEFAULT 0,
    remaining_budget NUMERIC(15, 2) NOT NULL DEFAULT 0,
    currency        TEXT NOT NULL DEFAULT 'INR',
    ai_summary      TEXT NOT NULL DEFAULT '',
    warnings        JSONB NOT NULL DEFAULT '[]'::JSONB,
    allocations     JSONB NOT NULL DEFAULT '[]'::JSONB,
    input_data      JSONB NOT NULL DEFAULT '{}'::JSONB,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'deleted')),
    partial         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER plans_updated_at
    BEFORE UPDATE ON plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE INDEX IF NOT EXISTS idx_plans_user_id       ON plans(user_id);
CREATE INDEX IF NOT EXISTS idx_plans_planner_type  ON plans(planner_type);
CREATE INDEX IF NOT EXISTS idx_plans_created_at    ON plans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_plans_user_created  ON plans(user_id, created_at DESC);

-- ============================================================
-- TABLE: recommendations
-- Recommendations generated for a plan.
-- ============================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id         UUID NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL DEFAULT '',
    source          TEXT,
    source_url      TEXT,
    price           NUMERIC(15, 2) NOT NULL DEFAULT 0,
    currency        TEXT NOT NULL DEFAULT 'INR',
    image_url       TEXT,
    description     TEXT NOT NULL DEFAULT '',
    why_recommended TEXT NOT NULL DEFAULT '',
    match_score     NUMERIC(5, 2) NOT NULL DEFAULT 0,
    budget_impact   TEXT NOT NULL DEFAULT 'medium'
                    CHECK (budget_impact IN ('low', 'medium', 'high')),
    metadata        JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommendations_plan_id ON recommendations(plan_id);

-- ============================================================
-- TABLE: saved_recommendations
-- User-saved recommendations (bookmarks).
-- ============================================================
CREATE TABLE IF NOT EXISTS saved_recommendations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    recommendation_id   UUID NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_saved_user_recommendation UNIQUE (user_id, recommendation_id)
);

CREATE INDEX IF NOT EXISTS idx_saved_user_id              ON saved_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_recommendation_id    ON saved_recommendations(recommendation_id);

-- ============================================================
-- TABLE: uploaded_images
-- Tracks images uploaded to Supabase Storage.
-- ============================================================
CREATE TABLE IF NOT EXISTS uploaded_images (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id         UUID REFERENCES plans(id) ON DELETE SET NULL,
    storage_path    TEXT NOT NULL,
    mime_type       TEXT NOT NULL,
    file_size       INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_uploaded_images_user_id  ON uploaded_images(user_id);
CREATE INDEX IF NOT EXISTS idx_uploaded_images_plan_id  ON uploaded_images(plan_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

-- profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- plans
ALTER TABLE plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own plans"
    ON plans FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own plans"
    ON plans FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own plans"
    ON plans FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own plans"
    ON plans FOR DELETE
    USING (auth.uid() = user_id);

-- recommendations (accessible through owned plans only)
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view recommendations for their plans"
    ON recommendations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM plans
            WHERE plans.id = recommendations.plan_id
            AND plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert recommendations for their plans"
    ON recommendations FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM plans
            WHERE plans.id = plan_id
            AND plans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete recommendations for their plans"
    ON recommendations FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM plans
            WHERE plans.id = recommendations.plan_id
            AND plans.user_id = auth.uid()
        )
    );

-- saved_recommendations
ALTER TABLE saved_recommendations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their saved recommendations"
    ON saved_recommendations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can save recommendations"
    ON saved_recommendations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can unsave recommendations"
    ON saved_recommendations FOR DELETE
    USING (auth.uid() = user_id);

-- uploaded_images
ALTER TABLE uploaded_images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their uploaded images"
    ON uploaded_images FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their uploaded images"
    ON uploaded_images FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- STORAGE BUCKET (run via Supabase dashboard or management API)
-- ============================================================
-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('planner-images', 'planner-images', false)
-- ON CONFLICT (id) DO NOTHING;
--
-- Storage RLS policies should be configured via the Supabase dashboard
-- to restrict access to: auth.uid()::text = (storage.foldername(name))[1]

-- ============================================================
-- FUNCTION: auto-create profile on user sign-up
-- ============================================================
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
    INSERT INTO profiles (id, full_name)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();
