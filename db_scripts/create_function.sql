CREATE OR REPLACE FUNCTION get_user_chats(p_user_id INTEGER)
RETURNS TABLE(chat_id INTEGER, chat_name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.chat_name
    FROM chat c
    JOIN connect con ON c.id = con.chat_id
    WHERE con.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION unread_message_count(
    p_chat_id INTEGER,
    p_user_id INTEGER
) RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM message
        WHERE chat_id = p_chat_id
          AND is_read = FALSE
          AND sender_id != p_user_id
    );
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION channel_subscriber_count(p_channel_id INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*) FROM subscription
        WHERE channel_id = p_channel_id
    );
END;
$$ LANGUAGE plpgsql;
