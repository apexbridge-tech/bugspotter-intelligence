-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Optional: Create a test to verify
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE NOTICE 'pgvector extension successfully installed!';
    END IF;
END
$$;