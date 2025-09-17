-- Quote of the Day Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create development and test databases if they don't exist
SELECT 'CREATE DATABASE quote_of_the_day_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'quote_of_the_day_dev')\gexec

SELECT 'CREATE DATABASE quote_test_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'quote_test_db')\gexec

-- Create users if they don't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'quote_user') THEN

      CREATE ROLE quote_user LOGIN PASSWORD 'quote_password';
   END IF;
END
$do$;

DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'test_user') THEN

      CREATE ROLE test_user LOGIN PASSWORD 'test_password';
   END IF;
END
$do$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE quote_of_the_day_dev TO quote_user;
GRANT ALL PRIVILEGES ON DATABASE quote_test_db TO test_user;

-- Connect to development database and set up initial schema
\c quote_of_the_day_dev;

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO quote_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO quote_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO quote_user;

-- Create initial tables (these will be managed by Alembic migrations in production)
-- This is just for initial development setup

CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Sample table structure (will be replaced by proper migrations)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Connect to test database and set up similar structure
\c quote_test_db;

GRANT ALL ON SCHEMA public TO test_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO test_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO test_user;

CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);