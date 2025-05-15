--Последние 5 сообщений в чате--
SELECT id, sender_id, content_text, created_at
FROM message
WHERE chat_id = 1
ORDER BY created_at DESC
LIMIT 5 OFFSET 1;

--Чаты с ≥ 10 сообщениями--
SELECT chat_id, COUNT(*) AS msg_count
FROM message
GROUP BY chat_id
HAVING COUNT(*) >= 10;

--Пользователи без подписок--
SELECT u.id, u.username
FROM "User" u
LEFT JOIN subscription s ON u.id = s.user_id
WHERE s.channel_id IS NULL;

--Пользователь(ли) с макс. числом сообщений--
SELECT sender_id
FROM message
GROUP BY sender_id
HAVING COUNT(*) = (
    SELECT MAX(cnt) FROM (
        SELECT COUNT(*) AS cnt
        FROM message
        GROUP BY sender_id
    ) AS sub
);

--Сообщения авторов из списка активных--
SELECT *
FROM message
WHERE sender_id IN (
    SELECT author_id
    FROM post
    GROUP BY author_id
    HAVING SUM((
        SELECT COUNT(*) FROM subscription
        WHERE channel_id = post.channel_id
    )) > 100
);

--Чаты с непрочитанными сообщениями--
SELECT c.id, c.chat_name
FROM chat c
WHERE EXISTS (
    SELECT 1 FROM message m
    WHERE m.chat_id = c.id
      AND m.is_read = FALSE
);

--Пары пользователей из одного чата--
SELECT DISTINCT con1.user_id AS user_a,
                con2.user_id AS user_b,
                con1.chat_id
FROM connect con1
JOIN connect con2
  ON con1.chat_id = con2.chat_id
 AND con1.user_id < con2.user_id;

--Рейтинг каналов по числу подписчиков--
SELECT channel_id,
       COUNT(*) AS sub_count,
       RANK() OVER (ORDER BY COUNT(*) DESC) AS popularity_rank
FROM subscription
GROUP BY channel_id;

--Накопительное число сообщений в чате--
SELECT id,
       created_at,
       ROW_NUMBER() OVER (
         PARTITION BY chat_id
         ORDER BY created_at
       ) AS seq_in_chat
FROM message
WHERE chat_id = 1
ORDER BY created_at;

--Разница во времени между сообщениями--
SELECT id,
       created_at,
       EXTRACT(
         EPOCH FROM created_at 
         - LAG(created_at) OVER (
             PARTITION BY chat_id
             ORDER BY created_at
           )
       ) AS seconds_since_prev
FROM message
WHERE chat_id = 1
ORDER BY created_at;
