-- Create metabase metadata database
SELECT 'CREATE DATABASE metabase_meta OWNER btrc_admin'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'metabase_meta')\gexec

-- Enable PostGIS and UUID extensions on main database
\c btrc_qos_poc
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
