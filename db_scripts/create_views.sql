CREATE VIEW chat_view AS
SELECT 
    c.id AS chat_id,
    c.chat_name,
    c.created_at,
    COUNT(con.id) AS participants_count
FROM 
    chat c
LEFT JOIN 
    connect con ON c.id = con.chat_id
GROUP BY 
    c.id;


CREATE VIEW message_view AS
SELECT 
    m.id AS message_id,
    m.chat_id,
    c.chat_name,
    m.sender_id,
    u.username AS sender_username,
    m.is_read,
    m.content_text,
    m.created_at
FROM 
    message m
JOIN 
    chat c ON m.chat_id = c.id
JOIN 
    "User" u ON m.sender_id = u.id;
