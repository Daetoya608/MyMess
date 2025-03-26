\echo '1. Пользователи, зарегистрированные после 01.01.2025'
SELECT id, username, nickname, email, created_at
FROM "User"
WHERE created_at > '2025-01-01'
ORDER BY created_at DESC;

\echo '2. Количество пользователей в каждом чате (чаты с >3 пользователями)'
SELECT chat_id, COUNT(user_id) AS user_count
FROM Connect
GROUP BY chat_id
HAVING COUNT(user_id) > 3;

\echo '3. Сообщения с отправителем и чатом'
SELECT m.id AS message_id, m.content_text, m.sent_at, u.username AS sender, c.chat_name
FROM Message m
INNER JOIN "User" u ON m.sender_id = u.id
INNER JOIN Chat c ON m.chat_id = c.id
ORDER BY m.sent_at DESC;

\echo '4. Найти среднее количество сообщений в чатах'
SELECT AVG(msg_count) AS avg_messages_per_chat
FROM (
    SELECT chat_id, COUNT(*) AS msg_count
    FROM Message
    GROUP BY chat_id
) subquery;

\echo '5. Пользователи, не состоящие в чатах'
SELECT username
FROM "User" u
WHERE NOT EXISTS (
    SELECT 1 FROM Connect c WHERE c.user_id = u.id
);

\echo '6. Каналы с >5 подписчиками'
SELECT ch.channel_name, COUNT(s.user_id) AS subscribers_count
FROM Subscription s
JOIN Channel ch ON s.channel_id = ch.id
GROUP BY ch.channel_name
HAVING COUNT(s.user_id) > 5;

\echo '7. Последние 5 сообщений в чате 2'
SELECT content_text, sent_at
FROM Message
WHERE chat_id = 2
ORDER BY sent_at DESC
LIMIT 5;

\echo '8. Номер сообщения в каждом чате'
SELECT id, chat_id, sender_id, content_text, sent_at,
       RANK() OVER (PARTITION BY chat_id ORDER BY sent_at) AS message_rank
FROM Message;

\echo '9. Количество сообщений каждого пользователя'
SELECT sender_id, COUNT(*) AS message_count
FROM Message
GROUP BY sender_id
ORDER BY message_count DESC;

\echo '10. Найти пользователей, отправивших больше всего сообщений в каждом чате'
SELECT DISTINCT ON (m.chat_id) m.chat_id, u.username, COUNT(*) AS message_count
FROM Message m
JOIN "User" u ON m.sender_id = u.id
GROUP BY m.chat_id, u.username
ORDER BY m.chat_id, message_count DESC;
