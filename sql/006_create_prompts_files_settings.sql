-- Migration: Create prompts, files, settings tables
-- Run this in Supabase SQL Editor

-- Prompts table
CREATE TABLE IF NOT EXISTS prompts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Files table
CREATE TABLE IF NOT EXISTS files (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    original_name TEXT NOT NULL,
    mime_type TEXT,
    size INTEGER,
    path TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    theme TEXT DEFAULT 'dark',
    language TEXT DEFAULT 'en',
    notifications BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_prompts_project_user ON prompts (project_id, user_id);
CREATE INDEX IF NOT EXISTS idx_files_project_user ON files (project_id, user_id);
CREATE INDEX IF NOT EXISTS idx_settings_user ON settings (user_id);
