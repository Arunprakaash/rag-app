-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the tenants table
CREATE TABLE IF NOT EXISTS tenants (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Create the knowledge_base table with a foreign key to tenants
CREATE TABLE IF NOT EXISTS knowledge_base (
  id SERIAL PRIMARY KEY,
  tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  chunk_content TEXT NOT NULL,
  embedding vector,
  created_at TIMESTAMPTZ DEFAULT now()
);