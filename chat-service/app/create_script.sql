CREATE table if not exists "user" (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    nickname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    info_about_yourself TEXT DEFAULT ''
);

CREATE TABLE if not exists chat (
    id SERIAL PRIMARY KEY,
    chat_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE if not exists connect (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    chat_id INTEGER NOT NULL REFERENCES chat(id) ON DELETE CASCADE
);

CREATE TABLE if not exists message (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES chat(id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    content_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE if not exists message_version (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    content_text TEXT NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NULL
);

CREATE TABLE if not exists channel (
    id SERIAL PRIMARY KEY,
    channel_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE if not exists post (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channel(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    content_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE if not exists subscription (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    channel_id INTEGER NOT NULL REFERENCES channel(id) ON DELETE CASCADE,
    subscribed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
