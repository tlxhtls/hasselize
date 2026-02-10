-- Hasselize Database Schema
-- Initial migration for Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Camera Styles (LoRA configurations)
-- ============================================================================
CREATE TABLE public.camera_styles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    lora_path TEXT,
    lora_weight DECIMAL(3,2) DEFAULT 1.00,
    is_premium BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert camera styles
INSERT INTO public.camera_styles (slug, name, description, is_premium, display_order) VALUES
    ('hasselblad', 'Hasselblad X2D', 'Medium format photography with exceptional depth and 100MP look', false, 1),
    ('leica_m', 'Leica M Series', 'Iconic rangefinder look with high contrast and street photography aesthetic', true, 2),
    ('zeiss', 'Zeiss Lenses', 'Carl Zeiss sharpness, micro contrast, and T* coating clarity', true, 3),
    ('fujifilm_gfx', 'Fujifilm GFX', 'Large sensor medium format with Film Simulations and natural skin tones', true, 4);

-- ============================================================================
-- Prompts (versioned, A/B testing)
-- ============================================================================
CREATE TABLE public.prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version TEXT NOT NULL,
    camera_style_id UUID NOT NULL REFERENCES public.camera_styles(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    negative_prompt TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert base prompts for FLUX.1-Schnell
-- Prompts optimized for img2img with 256x256 resolution
INSERT INTO public.prompts (version, camera_style_id, content, negative_prompt, is_active)
SELECT
    '1.0',
    id,
    CASE slug
        WHEN 'hasselblad' THEN
            'medium format photography, hasselblad x2d 100mp, 80mm f/2.8 lens, creamy bokeh, exceptional sharpness, professional color grading, natural depth of field, large sensor look'
        WHEN 'leica_m' THEN
            'leica m rangefinder photography, summicron 35mm f/2 asph, high contrast, cinematic color, candid moments, film grain aesthetic, street photography'
        WHEN 'zeiss' THEN
            'zeiss otus 55mm f/1.4, exceptional sharpness, micro contrast, t* coating, natural colors, professional studio lighting, commercial photography'
        WHEN 'fujifilm_gfx' THEN
            'fujifilm gfx 100s medium format, 80mm f/1.7, film simulation velvia, large sensor look, natural skin tones, shallow depth of field, professional portrait'
    END,
    'blurry, noise, distorted, oversaturated, artificial lighting, poor composition, hdr, digital look, chromatic aberration',
    true
FROM public.camera_styles;

-- ============================================================================
-- User Profiles
-- ============================================================================
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium')),
    credits_remaining INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- Transformations (main data table)
-- ============================================================================
CREATE TABLE public.transformations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    camera_style_id UUID NOT NULL REFERENCES public.camera_styles(id),

    -- Input
    original_image_url TEXT NOT NULL,
    original_image_key TEXT NOT NULL,

    -- Output
    transformed_image_url TEXT NOT NULL,
    transformed_image_key TEXT NOT NULL,
    thumbnail_url TEXT,
    thumbnail_key TEXT,

    -- Metadata
    resolution_mode TEXT NOT NULL CHECK (resolution_mode IN ('preview', 'standard', 'high')),
    model_used TEXT NOT NULL CHECK (model_used IN ('z-image-turbo', 'flux-schnell')),
    processing_time_ms INTEGER,
    seed INTEGER,

    -- Status
    status TEXT DEFAULT 'completed' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_transformations_user_id ON public.transformations(user_id);
CREATE INDEX idx_transformations_created_at ON public.transformations(created_at DESC);
CREATE INDEX idx_transformations_status ON public.transformations(status);
CREATE INDEX idx_transformations_camera_style ON public.transformations(camera_style_id);

-- ============================================================================
-- Feed (public before/after)
-- ============================================================================
CREATE TABLE public.feed (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transformation_id UUID NOT NULL REFERENCES public.transformations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT false,
    likes_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(transformation_id)
);

-- Indexes
CREATE INDEX idx_feed_is_public ON public.feed(is_public);
CREATE INDEX idx_feed_created_at ON public.feed(created_at DESC);
CREATE INDEX idx_feed_user_id ON public.feed(user_id);

-- ============================================================================
-- Likes
-- ============================================================================
CREATE TABLE public.likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feed_id UUID NOT NULL REFERENCES public.feed(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(feed_id, user_id)
);

-- Index
CREATE INDEX idx_likes_user_id ON public.likes(user_id);

-- ============================================================================
-- Row Level Security (RLS)
-- ============================================================================

-- Profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Transformations
ALTER TABLE public.transformations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own transformations"
    ON public.transformations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own transformations"
    ON public.transformations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own transformations"
    ON public.transformations FOR UPDATE
    USING (auth.uid() = user_id);

-- Feed
ALTER TABLE public.feed ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view public feed"
    ON public.feed FOR SELECT
    USING (is_public = true);

CREATE POLICY "Users can view own feed items"
    ON public.feed FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own feed items"
    ON public.feed FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own feed items"
    ON public.feed FOR UPDATE
    USING (auth.uid() = user_id);

-- Likes
ALTER TABLE public.likes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view likes"
    ON public.likes FOR SELECT
    USING (true);

CREATE POLICY "Users can insert own likes"
    ON public.likes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own likes"
    ON public.likes FOR DELETE
    USING (auth.uid() = user_id);

-- Camera styles (public read)
ALTER TABLE public.camera_styles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view active camera styles"
    ON public.camera_styles FOR SELECT
    USING (is_active = true);

-- Prompts (public read for active)
ALTER TABLE public.prompts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view active prompts"
    ON public.prompts FOR SELECT
    USING (is_active = true);

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to profiles table
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to prompts table
CREATE TRIGGER update_prompts_updated_at
    BEFORE UPDATE ON public.prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to increment likes_count
CREATE OR REPLACE FUNCTION increment_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.feed SET likes_count = likes_count + 1 WHERE id = NEW.feed_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to increment likes when like is created
CREATE TRIGGER on_like_created
    AFTER INSERT ON public.likes
    FOR EACH ROW
    EXECUTE FUNCTION increment_likes_count();

-- Function to decrement likes_count
CREATE OR REPLACE FUNCTION decrement_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.feed SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = OLD.feed_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Trigger to decrement likes when like is deleted
CREATE TRIGGER on_like_deleted
    AFTER DELETE ON public.likes
    FOR EACH ROW
    EXECUTE FUNCTION decrement_likes_count();

-- ============================================================================
-- Storage Buckets (create via Supabase dashboard or API)
-- ============================================================================
-- Bucket names:
-- - original-images: User uploaded images
-- - transformed-images: AI transformed images
-- - thumbnails: Generated thumbnails
