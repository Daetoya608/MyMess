import sqlite3
import pandas as pd
import numpy as np
from faker import Faker
import random
import datetime
import matplotlib.pyplot as plt
from scipy.stats import chisquare, pearsonr, ttest_ind

# --- 1. Генерация и вставка синтетических данных (SQLite in-memory) ---
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

cursor.executescript(""" 
CREATE TABLE IF NOT EXISTS "user" ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    username TEXT NOT NULL UNIQUE, 
    nickname TEXT NOT NULL, 
    email TEXT NOT NULL UNIQUE, 
    info_about_yourself TEXT DEFAULT '' 
); 
CREATE TABLE IF NOT EXISTS chat ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    chat_name TEXT NOT NULL, 
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
); 
CREATE TABLE IF NOT EXISTS channel ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    channel_name TEXT NOT NULL UNIQUE, 
    description TEXT, 
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    owner_id INTEGER NOT NULL 
); 
CREATE TABLE IF NOT EXISTS connect ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_id INTEGER NOT NULL, 
    chat_id INTEGER NOT NULL 
); 
CREATE TABLE IF NOT EXISTS message ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    chat_id INTEGER NOT NULL, 
    sender_id INTEGER NOT NULL, 
    is_read BOOLEAN NOT NULL DEFAULT FALSE, 
    content_text TEXT NOT NULL, 
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
); 
CREATE TABLE IF NOT EXISTS message_version ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    message_id INTEGER NOT NULL, 
    content_text TEXT NOT NULL, 
    valid_from TIMESTAMP NOT NULL, 
    valid_to TIMESTAMP NULL 
); 
CREATE TABLE IF NOT EXISTS post ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    channel_id INTEGER NOT NULL, 
    author_id INTEGER NOT NULL, 
    content_text TEXT NOT NULL, 
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
); 
CREATE TABLE IF NOT EXISTS subscription ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_id INTEGER NOT NULL, 
    channel_id INTEGER NOT NULL, 
    subscribed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
); 
""")

fake = Faker()
users = [(fake.user_name(), fake.first_name(), fake.email(), fake.text(max_nb_chars=20))
         for _ in range(50)]
cursor.executemany(
    "INSERT INTO \"user\" (username,nickname,email,info_about_yourself) VALUES (?,?,?,?)",
    users
)
chats = [(fake.word() + "_chat", fake.date_time_between('-1y', 'now').isoformat(' '))
         for _ in range(10)]
cursor.executemany("INSERT INTO chat (chat_name,created_at) VALUES (?,?)", chats)
for uid in range(1, 51):
    for cid in random.sample(range(1, 11), k=random.randint(1, 3)):
        cursor.execute("INSERT INTO connect (user_id,chat_id) VALUES (?,?)", (uid, cid))
channels = [(fake.word() + "_channel", fake.sentence(nb_words=4),
             fake.date_time_between('-1y', 'now').isoformat(' '),
             random.randint(1, 50)) for _ in range(5)]
cursor.executemany("INSERT INTO channel (channel_name,description,created_at,owner_id) VALUES (?,?,?,?)", channels)
for _ in range(80):
    cursor.execute("INSERT INTO subscription (user_id,channel_id) VALUES (?,?)",
                   (random.randint(1, 50), random.randint(1, 5)))
for _ in range(150):
    cursor.execute("INSERT INTO post (channel_id,author_id,content_text,created_at) VALUES (?,?,?,?)",
                   (random.randint(1, 5), random.randint(1, 50),
                    fake.text(max_nb_chars=100),
                    fake.date_time_between('-1y', 'now').isoformat(' ')))
messages = []
for _ in range(300):
    cid = random.randint(1, 10);
    uid = random.randint(1, 50)
    created = fake.date_time_between('-30d', 'now').isoformat(' ')
    content = fake.text(max_nb_chars=200)
    is_read = random.choice([0, 1])
    cursor.execute("INSERT INTO message (chat_id,sender_id,is_read,content_text,created_at) VALUES (?,?,?,?,?)",
                   (cid, uid, is_read, content, created))
    mid = cursor.lastrowid
    messages.append((mid, created, content))
    if random.random() < 0.2:
        dt = datetime.datetime.fromisoformat(created)
        edit = dt + datetime.timedelta(minutes=random.randint(1, 1440))
        new_text = fake.text(max_nb_chars=200)
        cursor.execute("INSERT INTO message_version (message_id,content_text,valid_from,valid_to) VALUES (?,?,?,NULL)",
                       (mid, new_text, edit.isoformat(' ')))
    conn.commit()

    # --- 2. Извлечение и агрегация данных ---
    msg_per_user = pd.read_sql_query(
        "SELECT sender_id, COUNT(*) AS num_messages FROM message GROUP BY sender_id", conn
    )
    subs_posts = pd.read_sql_query(""" 
        SELECT u.id AS user_id, 
               COALESCE(s.count_subs,0) AS num_subs, 
               COALESCE(p.count_posts,0) AS num_posts 
        FROM "user" u 
        LEFT JOIN (SELECT user_id, COUNT(*) AS count_subs FROM subscription GROUP BY user_id) s ON u.id=s.user_id 
        LEFT JOIN (SELECT author_id, COUNT(*) AS count_posts FROM post GROUP BY author_id) p ON u.id=p.author_id 
        """, conn)
    all_msgs = pd.read_sql_query("SELECT id, LENGTH(content_text) AS length FROM message", conn)
    edited = pd.read_sql_query("SELECT DISTINCT message_id FROM message_version", conn)
    all_msgs['edited'] = all_msgs['id'].isin(edited['message_id'])

    chi_stat, chi_p = chisquare(msg_per_user['num_messages'])
    corr_r, corr_p = pearsonr(subs_posts['num_subs'], subs_posts['num_posts'])
    t_stat, t_p = ttest_ind(
        all_msgs[all_msgs['edited']]['length'],
        all_msgs[~all_msgs['edited']]['length'],
        equal_var=False
    )

    # --- 3. Графики ---
    plt.figure()
    plt.hist(msg_per_user['num_messages'], bins=15)
    plt.title('Гистограмма: сообщений на пользователя')
    plt.xlabel('Число сообщений')
    plt.ylabel('Частота')
    plt.show()

    plt.figure()
    plt.scatter(subs_posts['num_subs'], subs_posts['num_posts'])
    plt.title('Подписки vs Посты на пользователя')
    plt.xlabel('Число подписок')
    plt.ylabel('Число постов')
    plt.show()

    plt.figure()
    data = [all_msgs[all_msgs['edited']]['length'], all_msgs[~all_msgs['edited']]['length']]
    plt.boxplot(data, labels=['edited', 'unedited'])
    plt.title('Сравнение длины сообщений')
    plt.ylabel('Длина текста')
    plt.show()

    # --- 4. Выводы ---
    print("H1 (распределение сообщений): χ² =", round(chi_stat, 2), "p =", round(chi_p, 3))
    print("H2 (корреляция подписки-посты): r =", round(corr_r, 2), "p =", round(corr_p, 3))
    print("H3 (длина редактированных vs нет): t =", round(t_stat, 2), "p =", round(t_p, 3))

    print("\nВыводы:")
    if chi_p > 0.05:
        print("- Распределение числа сообщений по пользователям близко к равномерному (p>0.05).")
    else:
        print("- Есть значимое отклонение в распределении сообщений (p<0.05).")
    if corr_p < 0.05:
        print(f"- Обнаружена корреляция подписок и постов (r={corr_r:.2f}).")
    else:
        print("- Корреляции подписок и постов не обнаружено (p>0.05).")
    if t_p < 0.05:
        print("- Редактированные сообщения значительно длиннее (p<0.05).")
    else:
        print("- Разницы в длине сообщений нет (p>0.05).")


"""анализ:
 • Графики:
 1. Гистограмма распределения числа сообщений на пользователя,
 2. Точечный график «подписки vs посты»,
 3. Box-plot сравнения длины редактированных и нередактированных сообщений.
 • Гипотезы:
 1. H1: числа сообщений распределены равномерно по пользователям (χ²-тест).
 2. H2: есть корреляция между числом подписок и числом постов (коэффициент Пирсона).
 3. H3: редактированные сообщения длиннее нередактированных (t-тест).
 • Результаты:
 • H1: χ² = 39.0, p = 0.846 → нет отклонения от равномерности.
 • H2: r = -0.24, p = 0.088 → корреляции нет.
 • H3: t = -1.29, p = 0.201 → разницы в длине нет.

Выводы:
Распределение активности пользователей по сообщениям выглядит равномерным,
связи между подписками и активностью в постах не выявлено, а редактирование
не влияет на длину сообщения."""
