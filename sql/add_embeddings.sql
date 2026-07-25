-- Migration: Add embeddings column to training_data
-- Run this in Supabase SQL Editor

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing embeddings column if it exists
ALTER TABLE training_data DROP COLUMN IF EXISTS embeddings;

-- Add embeddings column (768 dimensions for TF-IDF)
ALTER TABLE training_data ADD COLUMN embeddings vector(768);

-- Create index for faster vector search
CREATE INDEX IF NOT EXISTS idx_training_data_embeddings 
ON training_data USING hnsw (embeddings vector_cosine_ops);

-- Create composite index for project and user lookups
CREATE INDEX IF NOT EXISTS idx_training_data_project_user 
ON training_data (project_id, user_id);
