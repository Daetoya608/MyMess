CREATE OR REPLACE PROCEDURE send_message(
    IN p_chat_id INTEGER,
    IN p_sender_id INTEGER,
    IN p_content TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO message(chat_id, sender_id, content_text)
    VALUES (p_chat_id, p_sender_id, p_content);
END;
$$;


CREATE OR REPLACE PROCEDURE subscribe_user_to_channel(
    IN p_user_id INTEGER,
    IN p_channel_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM subscription
        WHERE user_id = p_user_id AND channel_id = p_channel_id
    ) THEN
        INSERT INTO subscription(user_id, channel_id)
        VALUES (p_user_id, p_channel_id);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE create_chat_with_user(
    IN p_chat_name TEXT,
    IN p_user_id INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    new_chat_id INTEGER;
BEGIN
    INSERT INTO chat(chat_name) VALUES (p_chat_name)
    RETURNING id INTO new_chat_id;

    INSERT INTO connect(chat_id, user_id)
    VALUES (new_chat_id, p_user_id);
END;
$$;
