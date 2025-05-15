import os
import psycopg2
import pytest
from datetime import datetime, date

@pytest.fixture(scope="module")
def conn():
    """Set up a PostgreSQL in-memory test database, create schema, insert sample data."""
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        database=os.getenv("PGDATABASE", "testdb"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "")
    )
    cur = conn.cursor()
    # create schema
    cur.execute("""
    CREATE TABLE IF NOT EXISTS "user" (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        nickname TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        info_about_yourself TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS chat (
        id SERIAL PRIMARY KEY,
        chat_name TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS connect (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
        chat_id INTEGER NOT NULL REFERENCES chat(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS message (
        id SERIAL PRIMARY KEY,
        chat_id INTEGER NOT NULL REFERENCES chat(id) ON DELETE CASCADE,
        sender_id INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
        is_read BOOLEAN NOT NULL DEFAULT FALSE,
        content_text TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS message_version (
        id SERIAL PRIMARY KEY,
        message_id INTEGER NOT NULL REFERENCES message(id) ON DELETE CASCADE,
        content_text TEXT NOT NULL,
        valid_from TIMESTAMP NOT NULL,
        valid_to TIMESTAMP NULL
    );
    CREATE TABLE IF NOT EXISTS channel (
        id SERIAL PRIMARY KEY,
        channel_name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        owner_id INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS post (
        id SERIAL PRIMARY KEY,
        channel_id INTEGER NOT NULL REFERENCES channel(id) ON DELETE CASCADE,
        author_id INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
        content_text TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS subscription (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
        channel_id INTEGER NOT NULL REFERENCES channel(id) ON DELETE CASCADE,
        subscribed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # Insert deterministic sample data
    cur.execute("""
    INSERT INTO "User"(username,nickname,email) VALUES
      ('alice','Alice','alice@example.com'),
      ('bob','Bob','bob@example.com'),
      ('charlie','Charlie','charlie@example.com');
    INSERT INTO chat(chat_name) VALUES ('chat1'), ('chat2');
    INSERT INTO connect(user_id,chat_id) VALUES (1,1), (2,1), (1,2);
    INSERT INTO message(chat_id,sender_id,content_text,created_at) VALUES
      (1,1,'Hello','2025-05-14 10:00'),
      (1,2,'Hi','2025-05-14 11:00'),
      (1,1,'How are you?','2025-05-15 09:00');
    INSERT INTO message_version(message_id, content_text, valid_from, valid_to) VALUES
      (1,'Hello','2025-05-14 10:00','2025-05-14 10:05'),
      (1,'Hello!','2025-05-14 10:05',NULL);
    INSERT INTO channel(channel_name,description,owner_id) VALUES
      ('alice','Alice channel',1),
      ('bob','Bob channel',2);
    INSERT INTO subscription(user_id,channel_id) VALUES (1,1), (2,1), (2,2);
    INSERT INTO post(channel_id,author_id,content_text,created_at) VALUES
      (1,1,'Post1','2025-05-13 08:00'),
      (1,2,'Post2','2025-05-14 09:00'),
      (2,2,'Post3','2025-05-15 10:00');
    """)
    conn.commit()
    yield conn
    conn.rollback()
    cur.close()
    conn.close()


def load_query(n):
    """Helper to extract Query n from queries.sql by its comment marker."""
    with open("queries.sql") as f:
        content = f.read()
    parts = content.split(f"-- Query {n}:")
    assert len(parts) > 1, f"Query {n} not found"
    return parts[1].split("-- Query")[0].strip()


def test_query_1(conn):
    """
    Query 1: number of chats per user – expect
      [('alice', 2), ('bob', 1)]
    """
    cur = conn.cursor()
    cur.execute(load_query(1))
    assert cur.fetchall() == [('alice', 2), ('bob', 1)]


def test_query_2(conn):
    """
    Query 2: chats with no messages – expect only 'chat2'
    """
    cur = conn.cursor()
    cur.execute(load_query(2))
    rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0][1] == 'chat2'


def test_query_3(conn):
    """
    Query 3: latest message per user:
      user 1 -> 'How are you?', user 2 -> 'Hi'
    """
    cur = conn.cursor()
    cur.execute(load_query(3))
    results = set(cur.fetchall())
    expected = {
        (1, 'How are you?', datetime(2025, 5, 15, 9, 0)),
        (2, 'Hi', datetime(2025, 5, 14, 11, 0))
    }
    assert results == expected


def test_query_4(conn):
    """
    Query 4: daily message counts >1 – expect chat 1 on 2025-05-14 with count 2
    """
    cur = conn.cursor()
    cur.execute(load_query(4))
    row = cur.fetchone()
    assert row[0] == 1
    assert row[1] == date(2025, 5, 14)
    assert row[2] == 2


def test_query_5(conn):
    """
    Query 5: pairs of users sharing a chat – expect only (1,2,1)
    """
    cur = conn.cursor()
    cur.execute(load_query(5))
    assert cur.fetchall() == [(1, 2, 1)]


def test_query_6(conn):
    """
    Query 6: message version changes – expect old 'Hello' -> new 'Hello!'
    """
    cur = conn.cursor()
    cur.execute(load_query(6))
    assert cur.fetchall() == [(1, 'Hello', 'Hello!')]


def test_query_7(conn):
    """
    Query 7: full outer join connect/subscription – expect 4 rows, user_ids {1,2}
    """
    cur = conn.cursor()
    cur.execute(load_query(7))
    rows = cur.fetchall()
    assert len(rows) == 4
    assert {r[0] for r in rows} == {1, 2}


def test_query_8(conn):
    """
    Query 8: channel(s) with max posts – expect (1,2)
    """
    cur = conn.cursor()
    cur.execute(load_query(8))
    assert cur.fetchall() == [(1, 2)]


def test_query_9(conn):
    """
    Query 9: users in chat 1 – expect {'alice','bob'}
    """
    cur = conn.cursor()
    cur.execute(load_query(9))
    assert {r[0] for r in cur.fetchall()} == {'alice', 'bob'}


def test_query_10(conn):
    """
    Query 10: rank authors by posts per channel – expect
      {(1,1,1,1),(1,2,1,1),(2,2,1,1)}
    """
    cur = conn.cursor()
    cur.execute(load_query(10))
    assert set(cur.fetchall()) == {
        (1, 1, 1, 1),
        (1, 2, 1, 1),
        (2, 2, 1, 1)
    }