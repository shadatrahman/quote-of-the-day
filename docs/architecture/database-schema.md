# Database Schema

```sql
-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search extension
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users table with authentication and subscription info
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(20) DEFAULT 'FREE' CHECK (subscription_tier IN ('FREE', 'PREMIUM')),
    timezone VARCHAR(50) DEFAULT 'UTC',
    last_quote_delivered TIMESTAMPTZ,
    fcm_device_token TEXT,

    -- Notification settings as JSONB for flexibility
    notification_settings JSONB DEFAULT '{
        "enabled": true,
        "delivery_time": "08:00",
        "weekdays_only": false,
        "pause_until": null
    }'::jsonb
);

-- Quotes table with full-text search optimization
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    author VARCHAR(255) NOT NULL,
    source VARCHAR(500),
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'LEADERSHIP', 'PHILOSOPHY', 'BUSINESS', 'CREATIVITY', 'WISDOM', 'DECISION_MAKING'
    )),
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    curator_notes TEXT,
    copyright_status VARCHAR(100) DEFAULT 'PUBLIC_DOMAIN',

    -- Full-text search vector for content and author
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', content), 'A') ||
        setweight(to_tsvector('english', author), 'B') ||
        setweight(to_tsvector('english', COALESCE(source, '')), 'C')
    ) STORED
);

-- User quote history for delivery tracking and analytics
CREATE TABLE user_quote_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quote_id UUID REFERENCES quotes(id) ON DELETE CASCADE,
    delivered_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    viewed_at TIMESTAMPTZ,
    starred_at TIMESTAMPTZ,
    engagement_score DECIMAL(3,2) DEFAULT 0.0,

    -- Ensure one delivery record per user per quote
    UNIQUE(user_id, quote_id)
);

-- Subscriptions table for premium tier management
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('FREE', 'PREMIUM')),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN (
        'ACTIVE', 'CANCELLED', 'PAST_DUE', 'INCOMPLETE', 'TRIALING'
    )),
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMPTZ
);

-- A/B testing experiments table for conversion optimization
CREATE TABLE ab_experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    variants JSONB NOT NULL, -- Array of variant configurations
    traffic_split JSONB DEFAULT '{"control": 0.5, "variant": 0.5}'::jsonb,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- User experiment assignments for A/B testing
CREATE TABLE user_experiment_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    experiment_id UUID REFERENCES ab_experiments(id) ON DELETE CASCADE,
    variant VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- One assignment per user per experiment
    UNIQUE(user_id, experiment_id)
);

-- Analytics events for user behavior tracking
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Performance-critical indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX idx_users_notification_time ON users((notification_settings->>'delivery_time'));
CREATE INDEX idx_users_active_fcm ON users(fcm_device_token) WHERE is_active = TRUE AND fcm_device_token IS NOT NULL;

CREATE INDEX idx_quotes_category ON quotes(category);
CREATE INDEX idx_quotes_active ON quotes(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_quotes_search_vector ON quotes USING GIN(search_vector);
CREATE INDEX idx_quotes_difficulty ON quotes(difficulty_level);

CREATE INDEX idx_user_quote_history_user_delivered ON user_quote_history(user_id, delivered_at DESC);
CREATE INDEX idx_user_quote_history_starred ON user_quote_history(user_id, starred_at) WHERE starred_at IS NOT NULL;
CREATE INDEX idx_user_quote_history_engagement ON user_quote_history(user_id, engagement_score DESC);

CREATE INDEX idx_subscriptions_user_status ON subscriptions(user_id, status);
CREATE INDEX idx_subscriptions_stripe_customer ON subscriptions(stripe_customer_id);

CREATE INDEX idx_analytics_events_user_type_time ON analytics_events(user_id, event_type, created_at DESC);
CREATE INDEX idx_analytics_events_type_time ON analytics_events(event_type, created_at DESC);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quotes_updated_at BEFORE UPDATE ON quotes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW active_premium_users AS
SELECT u.id, u.email, u.created_at, u.notification_settings
FROM users u
JOIN subscriptions s ON u.id = s.user_id
WHERE u.is_active = TRUE
  AND s.status = 'ACTIVE'
  AND s.tier = 'PREMIUM';

CREATE VIEW daily_quote_candidates AS
SELECT u.id as user_id, u.notification_settings, u.timezone,
       COALESCE(MAX(uqh.delivered_at), u.created_at) as last_quote_time
FROM users u
LEFT JOIN user_quote_history uqh ON u.id = uqh.user_id
WHERE u.is_active = TRUE
  AND (u.notification_settings->>'enabled')::boolean = TRUE
GROUP BY u.id, u.notification_settings, u.timezone;

-- Function to create monthly partitions for analytics
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name text, start_date date)
RETURNS void AS $$
DECLARE
    partition_name text;
    end_date date;
BEGIN
    partition_name := table_name || '_' || to_char(start_date, 'YYYY_MM');
    end_date := start_date + interval '1 month';

    EXECUTE format('CREATE TABLE %I PARTITION OF %I
                    FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);

    EXECUTE format('CREATE INDEX %I ON %I (user_id, created_at DESC)',
                   'idx_' || partition_name || '_user_time', partition_name);
END;
$$ LANGUAGE plpgsql;

-- Initial partition for current month
SELECT create_monthly_partition('analytics_events', date_trunc('month', CURRENT_DATE));
```
