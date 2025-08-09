-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS post_comment_likes CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS post_likes CASCADE;
DROP TABLE IF EXISTS Posts CASCADE;
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS followers CASCADE;
DROP TABLE IF EXISTS media CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop sequences if they exist
DROP SEQUENCE IF EXISTS users_id_seq CASCADE;
DROP SEQUENCE IF EXISTS posts_id_seq CASCADE;
DROP SEQUENCE IF EXISTS ratings_id_seq CASCADE;
DROP SEQUENCE IF EXISTS followers_id_seq CASCADE;
DROP SEQUENCE IF EXISTS post_likes_id_seq CASCADE;
DROP SEQUENCE IF EXISTS comments_id_seq CASCADE;
DROP SEQUENCE IF EXISTS post_comment_likes_id_seq CASCADE;
DROP SEQUENCE IF EXISTS media_id_seq CASCADE;

-- Create sequences for each table
CREATE SEQUENCE users_id_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE NO CYCLE CACHE 1;
CREATE SEQUENCE posts_id_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE NO CYCLE CACHE 1;
CREATE SEQUENCE ratings_id_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE NO CYCLE CACHE 1;
CREATE SEQUENCE followers_id_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE NO CYCLE CACHE 1;
CREATE SEQUENCE post_likes_id_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE NO CYCLE CACHE 1;
CREATE SEQUENCE comments_id_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE NO CYCLE CACHE 1;
CREATE SEQUENCE post_comment_likes_id_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE NO CYCLE CACHE 1;
CREATE SEQUENCE media_id_seq START WITH 1 INCREMENT BY 1 NO MAXVALUE NO CYCLE CACHE 1;

-- Create media table first as it's referenced by users
CREATE TABLE media (
    id BIGINT NOT NULL DEFAULT nextval('media_id_seq') PRIMARY KEY,
    context_id BIGINT,
    context_type VARCHAR(255),
    media_type VARCHAR(255),
    media_url TEXT,
    media_order INT,
    media_size BIGINT,
    caption TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE users (
    id BIGINT NOT NULL DEFAULT nextval('users_id_seq') PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50),
    address VARCHAR(255),
    latitude float,
    longitude float,
    bio TEXT,
    password VARCHAR(100) NOT NULL,
    isactive boolean DEFAULT true,
    email_verified boolean DEFAULT false,
    phone_verified boolean DEFAULT false,
    gst_no VARCHAR(255),
    cover_photo_id BIGINT NULL,
    profile_photo_id BIGINT NULL,
    last_login_at TIMESTAMP,
    CONSTRAINT fk_user_cover_photo FOREIGN KEY (cover_photo_id) 
        REFERENCES media(id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    CONSTRAINT fk_user_profile_photo FOREIGN KEY (profile_photo_id) 
        REFERENCES media(id) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Posts table (updated per new design)
CREATE TABLE Posts (
    id BIGINT NOT NULL DEFAULT nextval('posts_id_seq') PRIMARY KEY,
    user_id BIGINT NOT NULL,
    content VARCHAR(2000),
    title VARCHAR(255),
    visibility VARCHAR(50),
    "type" VARCHAR(50),
    location TEXT,
    map_location VARCHAR(100),
    price NUMERIC(15,2),
    status VARCHAR(50),
    is_anonymous BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


-- Create ratings table (renamed from user_ratings)
CREATE TABLE ratings (
    id BIGINT NOT NULL DEFAULT nextval('ratings_id_seq') PRIMARY KEY,
    rated_user_id BIGINT NOT NULL,
    rated_by_user_id BIGINT NOT NULL,
    rating_value INT CHECK (rating_value BETWEEN 1 AND 5),
    title VARCHAR(255),
    review TEXT,
    rating_type VARCHAR(255),
    is_anonymous boolean DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rated_user_id) REFERENCES users(id),
    FOREIGN KEY (rated_by_user_id) REFERENCES users(id)
);

-- Create followers table (renamed from user_followers)
CREATE TABLE followers (
    id BIGINT NOT NULL DEFAULT nextval('followers_id_seq') PRIMARY KEY,
    follower_id BIGINT NOT NULL,
    following_id BIGINT NOT NULL,
    followee_type VARCHAR(255),
    status VARCHAR(255) DEFAULT 'active',
    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (follower_id) REFERENCES users(id),
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

-- Create Comments table (updated per new design)
CREATE TABLE Comments (
    id BIGINT NOT NULL DEFAULT nextval('comments_id_seq') PRIMARY KEY,
    post_id BIGINT NOT NULL,
    parent_comment_id BIGINT NULL,
    comment VARCHAR(1000),
    user_id BIGINT NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    is_anonymous BOOLEAN DEFAULT false,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Posts(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES Comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_parent_comment CHECK (parent_comment_id IS NULL OR parent_comment_id > 0)
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
CREATE INDEX idx_media_context_id ON media(context_id);
CREATE INDEX idx_media_context_type ON media(context_type);
CREATE INDEX idx_users_profile_photo_id ON users(profile_photo_id);
CREATE INDEX idx_users_cover_photo_id ON users(cover_photo_id);
CREATE INDEX idx_posts_user_id ON Posts(user_id);
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