-- =====================================================
-- COMPLETE DATABASE SCHEMA FOR CHATBOT BACKEND
-- Creates tables only if they don't exist
-- =====================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- =====================================================
-- PROJECTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    model TEXT NOT NULL DEFAULT 'gemini-flash-latest',
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- =====================================================
-- TRAINING DATA TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS training_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('text', 'pdf')),
    file_name TEXT,
    metadata JSONB DEFAULT '{}',
    embeddings vector(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_training_data_project_id ON training_data(project_id);
CREATE INDEX IF NOT EXISTS idx_training_data_user_id ON training_data(user_id);
CREATE INDEX IF NOT EXISTS idx_training_data_embeddings ON training_data USING hnsw (embeddings vector_cosine_ops);

-- =====================================================
-- CONVERSATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT DEFAULT 'New Chat',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_project_id ON conversations(project_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- =====================================================
-- MESSAGES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- =====================================================
-- PROMPTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prompts_project_id ON prompts(project_id);
CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompts(user_id);

-- =====================================================
-- FILES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    original_name TEXT NOT NULL,
    mime_type TEXT,
    size INTEGER,
    path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id);
CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);

-- =====================================================
-- SETTINGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    theme TEXT DEFAULT 'dark',
    language TEXT DEFAULT 'en',
    notifications BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_settings_user_id ON settings(user_id);

-- =====================================================
-- VECTOR SEARCH FUNCTION
-- =====================================================
CREATE OR REPLACE FUNCTION match_training_data(
    query_embedding vector(768),
    p_project_id uuid,
    p_user_id uuid,
    match_count int DEFAULT 5,
    match_threshold float DEFAULT 0.5
)
RETURNS TABLE (
    id uuid,
    content text,
    type text,
    file_name text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        td.id,
        td.content,
        td.type,
        td.file_name,
        1 - (td.embeddings <=> query_embedding) AS similarity
    FROM training_data td
    WHERE td.project_id = p_project_id
        AND td.user_id = p_user_id
        AND td.embeddings IS NOT NULL
        AND 1 - (td.embeddings <=> query_embedding) > match_threshold
    ORDER BY td.embeddings <=> query_embedding
    LIMIT match_count;
END;
$$;
