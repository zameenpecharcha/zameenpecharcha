-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS post_comment_likes CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS post_likes CASCADE;
DROP TABLE IF EXISTS post_media CASCADE;
DROP TABLE IF EXISTS Posts CASCADE;
DROP TABLE IF EXISTS user_ratings CASCADE;
DROP TABLE IF EXISTS user_followers CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop sequences if they exist
DROP SEQUENCE IF EXISTS users_id_seq CASCADE;
DROP SEQUENCE IF EXISTS posts_id_seq CASCADE;
DROP SEQUENCE IF EXISTS post_media_id_seq CASCADE;
DROP SEQUENCE IF EXISTS user_ratings_id_seq CASCADE;
DROP SEQUENCE IF EXISTS user_followers_id_seq CASCADE;
DROP SEQUENCE IF EXISTS post_likes_id_seq CASCADE;
DROP SEQUENCE IF EXISTS comments_id_seq CASCADE;
DROP SEQUENCE IF EXISTS post_comment_likes_id_seq CASCADE;

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

CREATE SEQUENCE user_ratings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE
    CACHE 1;

CREATE SEQUENCE user_followers_id_seq
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
    content VARCHAR(2000),
    title VARCHAR(255),
    visibility VARCHAR(20),
    property_type VARCHAR(50),
    location VARCHAR(255),
    map_location VARCHAR(100),
    price NUMERIC(15,2),
    status VARCHAR(20),
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

-- Create user_ratings table
CREATE TABLE user_ratings (
    id BIGINT NOT NULL DEFAULT nextval('user_ratings_id_seq') PRIMARY KEY,
    rated_user_id BIGINT NOT NULL,
    rated_by_user_id BIGINT NOT NULL,
    rating_value INT CHECK (rating_value BETWEEN 1 AND 5),
    review TEXT,
    rating_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rated_user_id) REFERENCES users(id),
    FOREIGN KEY (rated_by_user_id) REFERENCES users(id)
);

-- Create user_followers table
CREATE TABLE user_followers (
    id BIGINT NOT NULL DEFAULT nextval('user_followers_id_seq') PRIMARY KEY,
    user_id BIGINT NOT NULL,
    following_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (following_id) REFERENCES users(id)
);

-- Create post_likes table
CREATE TABLE post_likes (
    id BIGINT NOT NULL DEFAULT nextval('post_likes_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    reaction_type VARCHAR(20),
    user_id BIGINT NOT NULL,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create Comments table
CREATE TABLE Comments (
    id BIGINT NOT NULL DEFAULT nextval('comments_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    parent_comment_id BIGINT,
    comment VARCHAR(1000),
    user_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(id),
    FOREIGN KEY (parent_comment_id) REFERENCES Comments(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create post_comment_likes table
CREATE TABLE post_comment_likes (
    id BIGINT NOT NULL DEFAULT nextval('post_comment_likes_id_seq') PRIMARY KEY,
    comment_id BIGINT NOT NULL,
    reaction_type VARCHAR(20),
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
CREATE INDEX idx_user_ratings_rated_user_id ON user_ratings(rated_user_id);
CREATE INDEX idx_user_ratings_rated_by_user_id ON user_ratings(rated_by_user_id);
CREATE INDEX idx_user_followers_user_id ON user_followers(user_id);
CREATE INDEX idx_user_followers_following_id ON user_followers(following_id);
CREATE INDEX idx_post_likes_post_id ON post_likes(post_id);
CREATE INDEX idx_post_likes_user_id ON post_likes(user_id);
CREATE INDEX idx_comments_post_id ON Comments(post_id);
CREATE INDEX idx_comments_user_id ON Comments(user_id);
CREATE INDEX idx_post_comment_likes_comment_id ON post_comment_likes(comment_id);
CREATE INDEX idx_post_comment_likes_user_id ON post_comment_likes(user_id); 