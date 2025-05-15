from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Boolean,
    ForeignKey, TIMESTAMP, func
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from faker import Faker
import random
import datetime
# 1. Настройка подключения и сессии
DATABASE_URL = "postgresql://postgres:0608@localhost/chat_db"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True для логирования SQL
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# 2. Описание моделей
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, nullable=False, unique=True)
    nickname = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    info_about_yourself = Column(Text, default="")

    chats = relationship("Connect", back_populates="user")
    channels = relationship("Channel", back_populates="owner")
    messages = relationship("Message", back_populates="sender")
    posts = relationship("Post", back_populates="author")
    subscriptions = relationship("Subscription", back_populates="user")

class Chat(Base):
    __tablename__ = "chat"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_name = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    users = relationship("Connect", back_populates="chat")
    messages = relationship("Message", back_populates="chat")

class Channel(Base):
    __tablename__ = "channel"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    owner = relationship("User", back_populates="channels")
    posts = relationship("Post", back_populates="channel")
    subscriptions = relationship("Subscription", back_populates="channel")

class Connect(Base):
    __tablename__ = "connect"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat.id"), nullable=False)

    user = relationship("User", back_populates="chats")
    chat = relationship("Chat", back_populates="users")

class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chat.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    content_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    versions = relationship("MessageVersion", back_populates="message")

class MessageVersion(Base):
    __tablename__ = "message_version"
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("message.id"), nullable=False)
    content_text = Column(Text, nullable=False)
    valid_from = Column(TIMESTAMP, nullable=False)
    valid_to = Column(TIMESTAMP)

    message = relationship("Message", back_populates="versions")

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channel.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    content_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    channel = relationship("Channel", back_populates="posts")
    author = relationship("User", back_populates="posts")

class Subscription(Base):
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channel.id"), nullable=False)
    subscribed_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="subscriptions")
    channel = relationship("Channel", back_populates="subscriptions")

# 3. Создаем таблицы (если не существуют)
Base.metadata.create_all(bind=engine)

# 4. Функция для вставки записи
def insert_record(session, model, **kwargs):
    """
    Пример использования:
      with SessionLocal() as db:
          insert_record(db, User, username="ivan", nickname="Иван", email="ivan@example.com")
    """
    obj = model(**kwargs)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj



# 2. Генерация и вставка синтетических данных
def generate_data(
    num_users=50,
    num_chats=10,
    num_messages=200,
    num_channels=5,
    num_posts=100,
    num_subscriptions=150
):
    fake = Faker()
    session = SessionLocal()
    try:
        # a) Пользователи
        users = []
        used_logins = set()
        for _ in range(num_users):
            while True:
                uname = fake.user_name()
                if uname not in used_logins:
                    used_logins.add(uname)
                    break
            users.append(User(
                username=uname,
                nickname=fake.first_name(),
                email=fake.email(),
                info_about_yourself=fake.text(max_nb_chars=50)
            ))
        session.add_all(users)
        session.flush()  # присвоит каждому id

        # b) Чаты
        chats = [
            Chat(chat_name=f"{fake.word()}_chat")
            for _ in range(num_chats)
        ]
        session.add_all(chats)
        session.flush()

        # c) Connect (пользователи ↔️ чаты)
        connects = []
        for u in users:
            # каждый пользователь в 1–3 случайных чатах
            for c in random.sample(chats, k=random.randint(1, 3)):
                connects.append(Connect(user_id=u.id, chat_id=c.id))
        session.add_all(connects)

        # d) Сообщения
        messages = []
        for _ in range(num_messages):
            c = random.choice(chats)
            u = random.choice(users)
            messages.append(Message(
                chat_id=c.id,
                sender_id=u.id,
                is_read=random.choice([True, False]),
                content_text=fake.text(max_nb_chars=200),
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            ))
        session.add_all(messages)
        session.flush()

        # e) Редактирования сообщений (20% сообщений)
        versions = []
        for m in messages:
            if random.random() < 0.2:
                edit_time = m.created_at + datetime.timedelta(
                    minutes=random.randint(1, 1440)
                )
                versions.append(MessageVersion(
                    message_id=m.id,
                    content_text=fake.text(max_nb_chars=200),
                    valid_from=edit_time,
                    valid_to=None
                ))
        session.add_all(versions)

        # f) Каналы и их подписчики + посты
        channels = [
            Channel(
                channel_name=f"{fake.word()}_channel",
                description=fake.sentence(),
                owner_id=random.choice(users).id
            )
            for _ in range(num_channels)
        ]
        session.add_all(channels)
        session.flush()

        subs = []
        posts = []
        for _ in range(num_subscriptions):
            subs.append(Subscription(
                user_id=random.choice(users).id,
                channel_id=random.choice(channels).id
            ))
        for _ in range(num_posts):
            posts.append(Post(
                channel_id=random.choice(channels).id,
                author_id=random.choice(users).id,
                content_text=fake.text(max_nb_chars=200),
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            ))
        session.add_all(subs + posts)

        # Коммит всех вставок
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# 3. Извлечение и агрегация данных
def aggregate_example():
    """
    Пример: для каждого пользователя посчитать число отправленных сообщений
    и среднюю длину его сообщений.
    """
    session = SessionLocal()
    try:
        q = (
            session.query(
                Message.sender_id.label("user_id"),
                func.count(Message.id).label("msg_count"),
                func.avg(func.length(Message.content_text)).label("avg_len")
            )
            .group_by(Message.sender_id)
            .subquery()
        )
        result = session.query(
            q.c.user_id, q.c.msg_count, q.c.avg_len
        ).all()

        for user_id, msg_count, avg_len in result:
            print(f"User {user_id}: messages={msg_count}, avg_length={avg_len:.1f}")
    finally:
        session.close()

if __name__ == "__main__":
    # Генерируем и вставляем данные
    # generate_data()

    # Извлекаем агрегированные данные
    aggregate_example()
