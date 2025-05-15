import pytest
import psycopg2
from psycopg2.extras import RealDictCursor

DSN = "dbname=chat_db user=postgres password=0608 host=localhost"

@pytest.fixture(scope="module")
def conn():
    conn = psycopg2.connect(DSN)
    conn.autocommit = True
    yield conn
    conn.close()

@pytest.fixture(scope="module", autouse=True)
def setup_schema(conn):
    """
    Создаёт схему из файла create.sql перед всеми тестами
    и опционально очищает её после.
    """
    cur = conn.cursor()
    # читаем и выполняем DDL
    with open("create_script.sql", "r", encoding="utf-8") as f:
        cur.execute(f.read())
    yield
    # если нужно — после тестов можно сбросить схему
    cur.execute("""
        DROP TABLE IF EXISTS subscription, post, message_version,
                         message, connect, chat, "user",
                         channel CASCADE;
    """)


@pytest.fixture(autouse=True)
def seed_data(conn):
    cur = conn.cursor()
    # Очищаем и наполняем минимальными данными
    cur.execute("""
        TRUNCATE subscription, post, message, connect, chat, "user" RESTART IDENTITY CASCADE;
        INSERT INTO "user"(username, nickname, email) VALUES
            ('alice','Al','a@e.com'),
            ('bob','B','b@e.com');
        INSERT INTO chat(chat_name) VALUES ('General');
        INSERT INTO connect(user_id, chat_id) VALUES (1,1),(2,1);
        INSERT INTO message(chat_id, sender_id, is_read, content_text, created_at) VALUES
          (1,1,TRUE,'Hi',  '2025-05-10 10:00'),
          (1,2,FALSE,'Hello','2025-05-10 10:05'),
          (1,1,FALSE,'How are you?','2025-05-10 10:10');
        INSERT INTO channel(channel_name, description, owner_id) VALUES ('news','News channel',1);
        INSERT INTO post(channel_id, author_id, content_text) VALUES (1,1,'Post1');
        INSERT INTO subscription(user_id, channel_id) VALUES (2,1),(1,1);
    """)
    yield
    # После каждого теста — чистим данные
    cur.execute("TRUNCATE subscription, post, message, connect, chat, \"user\" RESTART IDENTITY CASCADE;")

def run_query(conn, sql):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql)
        return cur.fetchall()

def test_1_last_messages(conn):
    """LIMIT/OFFSET + ORDER BY + WHERE — должны получить 2-ю по свежести запись."""
    rows = run_query(conn, """
        SELECT id FROM message
        WHERE chat_id = 1
        ORDER BY created_at DESC
        LIMIT 1 OFFSET 1;
    """)
    assert rows == [{'id': 2}]

def test_2_chats_with_min_msgs(conn):
    """GROUP BY + HAVING — ни один чат не имеет ≥ 10 сообщений."""
    rows = run_query(conn, """
        SELECT chat_id FROM message
        GROUP BY chat_id
        HAVING COUNT(*) >= 10;
    """)
    assert rows == []

def test_3_users_without_subs(conn):
    """LEFT JOIN + IS NULL — нет пользователей без подписок."""
    rows = run_query(conn, """
        SELECT u.id FROM "user" u
        LEFT JOIN subscription s ON u.id = s.user_id
        WHERE s.channel_id IS NULL;
    """)
    assert rows == []

def test_4_user_with_max_msgs(conn):
    """Скалярный подзапрос — максимум 2 сообщений у Alice (id=1)."""
    rows = run_query(conn, """
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
    """)
    assert rows == [{'sender_id': 1}]

def test_5_msgs_from_active_authors(conn):
    """Нескалярный подзапрос + IN — у автора 1 ровно 2 подписчика."""
    rows = run_query(conn, """
        SELECT * FROM message
        WHERE sender_id IN (
            SELECT author_id
            FROM post
            GROUP BY author_id
            HAVING SUM((
                SELECT COUNT(*) FROM subscription
                WHERE channel_id = post.channel_id
            )) > 1
        );
    """)
    # Должны вернуть все 3 сообщения Alice (sender_id=1)
    assert {r['id'] for r in rows} == {1,3}

def test_6_chats_with_unread(conn):
    """EXISTS — чат 1 содержит хотя бы одно непрочитанное."""
    rows = run_query(conn, """
        SELECT c.id FROM chat c
        WHERE EXISTS (
            SELECT 1 FROM message m
            WHERE m.chat_id = c.id AND m.is_read = FALSE
        );
    """)
    assert rows == [{'id': 1}]

def test_7_user_pairs_in_chat(conn):
    """Самосоединение — одна пара (1,2)."""
    rows = run_query(conn, """
        SELECT DISTINCT con1.user_id AS a, con2.user_id AS b
        FROM connect con1
        JOIN connect con2
          ON con1.chat_id = con2.chat_id
         AND con1.user_id < con2.user_id;
    """)
    assert rows == [{'a': 1, 'b': 2}]

def test_8_channel_rank(conn):
    """RANK() — единственный канал получает ранг 1."""
    rows = run_query(conn, """
        SELECT channel_id, popularity_rank FROM (
          SELECT channel_id,
                 RANK() OVER (ORDER BY COUNT(*) DESC) AS popularity_rank
          FROM subscription
          GROUP BY channel_id
        ) sub;
    """)
    assert rows == [{'channel_id': 1, 'popularity_rank': 1}]

def test_9_seq_in_chat(conn):
    """ROW_NUMBER() — три сообщения, последовательность 1,2,3."""
    rows = run_query(conn, """
        SELECT seq_in_chat FROM (
          SELECT ROW_NUMBER() OVER (
                   PARTITION BY chat_id
                   ORDER BY created_at
                 ) AS seq_in_chat
          FROM message
          WHERE chat_id = 1
        ) sub
        ORDER BY seq_in_chat;
    """)
    assert [r['seq_in_chat'] for r in rows] == [1,2,3]

def test_10_time_diff_lag(conn):
    """LAG() — проверяем, что первая разница NULL, вторая =300 сек."""
    rows = run_query(conn, """
        SELECT seconds_since_prev FROM (
          SELECT EXTRACT(
                   EPOCH FROM created_at - 
                   LAG(created_at) OVER (
                     PARTITION BY chat_id ORDER BY created_at
                   )
                 ) AS seconds_since_prev
          FROM message
          WHERE chat_id = 1
        ) sub
        ORDER BY seconds_since_prev NULLS FIRST;
    """)
    # Первая запись — NULL, вторая и третья — 300 сек
    assert rows[0]['seconds_since_prev'] is None
    assert rows[1]['seconds_since_prev'] == 300.0
    assert rows[2]['seconds_since_prev'] == 300.0
