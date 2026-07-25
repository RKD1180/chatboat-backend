-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embeddings column to training_data table (768 dimensions for TF-IDF)
ALTER TABLE training_data ADD COLUMN IF NOT EXISTS embeddings vector(768);

-- Create index for faster vector search
CREATE INDEX IF NOT EXISTS idx_training_data_embeddings 
ON training_data USING hnsw (embeddings vector_cosine_ops);

-- Create index for project and user lookups
CREATE INDEX IF NOT EXISTS idx_training_data_project_user 
ON training_data (project_id, user_id);
