-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS post_comment_likes CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS post_likes CASCADE;
DROP TABLE IF EXISTS post_media CASCADE;
DROP TABLE IF EXISTS Posts CASCADE;
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS followers CASCADE;
DROP TABLE IF EXISTS users CASCADE;
-- Drop property tables if they exist
DROP TABLE IF EXISTS user_property;
DROP TABLE IF EXISTS property_documents;
DROP TABLE IF EXISTS property_features;
DROP TABLE IF EXISTS media;
DROP TABLE IF EXISTS properties;


-- Drop sequences if they exist
DROP SEQUENCE IF EXISTS users_id_seq CASCADE;
DROP SEQUENCE IF EXISTS posts_id_seq CASCADE;
DROP SEQUENCE IF EXISTS post_media_id_seq CASCADE;
DROP SEQUENCE IF EXISTS ratings_id_seq CASCADE;
DROP SEQUENCE IF EXISTS followers_id_seq CASCADE;
DROP SEQUENCE IF EXISTS post_likes_id_seq CASCADE;
DROP SEQUENCE IF EXISTS comments_id_seq CASCADE;
DROP SEQUENCE IF EXISTS post_comment_likes_id_seq CASCADE;
DROP SEQUENCE IF EXISTS properties_id_seq;
DROP SEQUENCE IF EXISTS property_documents_id_seq;
DROP SEQUENCE IF EXISTS property_features_id_seq;
DROP SEQUENCE IF EXISTS media_id_seq;
DROP SEQUENCE IF EXISTS user_property_id_seq;

-- Drop custom domain if exists
DROP DOMAIN IF EXISTS Base64 CASCADE;

-- Create custom domain for Base64 encoded data
CREATE DOMAIN Base64 AS TEXT
    CHECK (length(value) > 0 AND length(value) % 4 = 0 AND value ~ '^[A-Za-z0-9+/]*[=]{0,2}$');

-- Create sequence for each table with MINVALUE 1 and NO CYCLE
CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

CREATE SEQUENCE posts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

CREATE SEQUENCE post_media_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

CREATE SEQUENCE ratings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

CREATE SEQUENCE followers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

CREATE SEQUENCE post_likes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

CREATE SEQUENCE comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

CREATE SEQUENCE post_comment_likes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

-- Create sequences
CREATE SEQUENCE properties_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE property_documents_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE property_features_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE media_id_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE user_property_id_seq START WITH 1 INCREMENT BY 1;

-- Create users table
CREATE TABLE users (
    id BIGINT NOT NULL DEFAULT nextval('users_id_seq') PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    profile_photo Base64,
    role VARCHAR(50),
    address VARCHAR(255),
    latitude float,
    longitude float,
    bio TEXT,
    password VARCHAR(100) NOT NULL,
    isactive boolean DEFAULT true,
    email_verified boolean DEFAULT false,
    phone_verified boolean DEFAULT false,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Posts table
CREATE TABLE Posts (
    id BIGINT NOT NULL DEFAULT nextval('posts_id_seq') PRIMARY KEY,
    user_id BIGINT NOT NULL,
    content VARCHAR,
    title VARCHAR,
    visibility VARCHAR,
    property_type VARCHAR,
    location TEXT,
    map_location VARCHAR,
    price NUMERIC(15,2),
    status VARCHAR,
    is_anonymous BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create post_media table
CREATE TABLE post_media (
    id BIGINT NOT NULL DEFAULT nextval('post_media_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    media_type VARCHAR(50),
    media_url TEXT,
    media_order INT,
    media_size BIGINT,
    caption TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(id)
);

-- Create ratings table (updated schema)
CREATE TABLE ratings (
    id BIGINT NOT NULL DEFAULT nextval('ratings_id_seq') PRIMARY KEY,
    rated_user_id BIGINT NOT NULL,
    rated_by_user_id BIGINT NOT NULL,
    rating_value INT CHECK (rating_value BETWEEN 1 AND 5),
    title VARCHAR,
    review TEXT,
    rating_type VARCHAR,
    is_anonymous BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rated_user_id) REFERENCES users(id),
    FOREIGN KEY (rated_by_user_id) REFERENCES users(id)
);

-- Create followers table (updated schema)
CREATE TABLE followers (
    id BIGINT NOT NULL DEFAULT nextval('followers_id_seq') PRIMARY KEY,
    follower_id BIGINT NOT NULL,
    following_id BIGINT NOT NULL,
    followee_type VARCHAR,
    status VARCHAR,
    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (follower_id) REFERENCES users(id),
    FOREIGN KEY (following_id) REFERENCES users(id)
);

-- Create post_likes table
CREATE TABLE post_likes (
    id BIGINT NOT NULL DEFAULT nextval('post_likes_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    reaction_type VARCHAR,
    user_id BIGINT NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create Comments table
CREATE TABLE Comments (
    id BIGINT NOT NULL DEFAULT nextval('comments_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    parent_comment_id BIGINT NULL,  -- NULL for top-level comments, actual ID for replies
    comment VARCHAR,
    user_id BIGINT NOT NULL,
    status VARCHAR,
    is_anonymous BOOLEAN DEFAULT false,
    edited_at TIMESTAMP,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES Comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_parent_comment CHECK (parent_comment_id IS NULL OR parent_comment_id > 0)  -- Ensure parent_comment_id is either NULL or a valid ID
);

-- Create post_comment_likes table
CREATE TABLE post_comment_likes (
    id BIGINT NOT NULL DEFAULT nextval('post_comment_likes_id_seq') PRIMARY KEY,
    comment_id BIGINT NOT NULL,
    reaction_type VARCHAR,
    user_id BIGINT NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES Comments(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add unique constraints
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);
ALTER TABLE users ADD CONSTRAINT users_phone_unique UNIQUE (phone);

-- Add indexes for better query performance
CREATE INDEX idx_posts_user_id ON Posts(user_id);
CREATE INDEX idx_post_media_post_id ON post_media(post_id);
CREATE INDEX idx_ratings_rated_user_id ON ratings(rated_user_id);
CREATE INDEX idx_ratings_rated_by_user_id ON ratings(rated_by_user_id);
CREATE INDEX idx_followers_follower_id ON followers(follower_id);
CREATE INDEX idx_followers_following_id ON followers(following_id);
CREATE INDEX idx_post_likes_post_id ON post_likes(post_id);
CREATE INDEX idx_post_likes_user_id ON post_likes(user_id);
CREATE INDEX idx_comments_post_id ON Comments(post_id);
CREATE INDEX idx_comments_user_id ON Comments(user_id);
CREATE INDEX idx_post_comment_likes_comment_id ON post_comment_likes(comment_id);
CREATE INDEX idx_post_comment_likes_user_id ON post_comment_likes(user_id); 

-- Property Service Tables


-- Create properties table
CREATE TABLE properties (
    id BIGINT PRIMARY KEY DEFAULT nextval('properties_id_seq'),
    title VARCHAR,
    builder_name VARCHAR,
    project_name VARCHAR,
    rera_id VARCHAR,
    year_build INTEGER,
    no_of_floors INTEGER,
    no_of_units INTEGER,
    building_amenities TEXT,
    verification_status VARCHAR,
    verified_by BIGINT,
    like_count INTEGER DEFAULT 0,
    is_flagged BOOLEAN DEFAULT FALSE,
    average_rating FLOAT DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    description VARCHAR,
    property_type VARCHAR,
    listing_type VARCHAR,
    price FLOAT,
    area_size FLOAT,
    bathroom_count INTEGER,
    construction_status VARCHAR,
    availability_date TIMESTAMP,
    location TEXT,
    city VARCHAR,
    state VARCHAR,
    country VARCHAR,
    pin_code VARCHAR,
    latitude FLOAT,
    longitude FLOAT,
    status VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create property_documents table
CREATE TABLE property_documents (
    id BIGINT PRIMARY KEY DEFAULT nextval('property_documents_id_seq'),
    property_id BIGINT NOT NULL,
    doc_name VARCHAR,
    doc_url TEXT,
    uploaded_by BIGINT,
    is_verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Create property_features table
CREATE TABLE property_features (
    id BIGINT PRIMARY KEY DEFAULT nextval('property_features_id_seq'),
    property_id BIGINT NOT NULL,
    feature_name VARCHAR,
    feature_value VARCHAR,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Create media table
CREATE TABLE media (
    id BIGINT PRIMARY KEY DEFAULT nextval('media_id_seq'),
    context_id BIGINT,
    context_type VARCHAR,
    media_type VARCHAR,
    media_url VARCHAR,
    media_order INTEGER DEFAULT 0,
    media_size INTEGER,
    caption TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_property table
CREATE TABLE user_property (
    id BIGINT PRIMARY KEY DEFAULT nextval('user_property_id_seq'),
    user_id BIGINT NOT NULL,
    property_id BIGINT NOT NULL,
    role VARCHAR,
    is_primary BOOLEAN DEFAULT FALSE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Create indexes for property tables
CREATE INDEX idx_properties_city ON properties(city);
CREATE INDEX idx_properties_state ON properties(state);
CREATE INDEX idx_properties_property_type ON properties(property_type);
CREATE INDEX idx_properties_listing_type ON properties(listing_type);
CREATE INDEX idx_properties_price ON properties(price);
CREATE INDEX idx_properties_verification_status ON properties(verification_status);
CREATE INDEX idx_properties_construction_status ON properties(construction_status);
CREATE INDEX idx_properties_created_at ON properties(created_at);
CREATE INDEX idx_property_documents_property_id ON property_documents(property_id);
CREATE INDEX idx_property_documents_uploaded_by ON property_documents(uploaded_by);
CREATE INDEX idx_property_features_property_id ON property_features(property_id);
CREATE INDEX idx_media_context ON media(context_id, context_type);
CREATE INDEX idx_media_uploaded_at ON media(uploaded_at);
CREATE INDEX idx_user_property_user_id ON user_property(user_id);
CREATE INDEX idx_user_property_property_id ON user_property(property_id);
CREATE INDEX idx_user_property_role ON user_property(role); 