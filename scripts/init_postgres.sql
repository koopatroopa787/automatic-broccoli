-- Initialize PostgreSQL database for analytics platform
-- This script is run on database initialization

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create extension for pg_trgm (for text search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Log initialization
SELECT 'Analytics database initialized successfully' AS status;
