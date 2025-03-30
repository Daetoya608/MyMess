SELECT AVG(msgcount)
FROM
(
SELECT chat_id, COUNT(*) as msgcount
FROM Message
GROUP BY chat_id
);
