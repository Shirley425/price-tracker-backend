CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tracked_items (
    tracked_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL,
    external_id VARCHAR(255),
    product_title VARCHAR(255) NOT NULL,
    product_url TEXT,
    image_url TEXT,
    target_price NUMERIC(10,2),
    current_price NUMERIC(10,2),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS price_history (
    price_history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracked_item_id UUID NOT NULL REFERENCES tracked_items(tracked_item_id) ON DELETE CASCADE,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price NUMERIC(10,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    source VARCHAR(100),
    fetch_status VARCHAR(50) NOT NULL,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    tracked_item_id UUID REFERENCES tracked_items(tracked_item_id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    message TEXT,
    sent_at TIMESTAMP,
    status VARCHAR(50) NOT NULL
);