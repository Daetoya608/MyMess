-- Ускоряет поиск сообщений по чату
CREATE INDEX idx_message_chat_id ON message(chat_id);

-- Ускоряет выборку сообщений от конкретного пользователя
CREATE INDEX idx_message_sender_id ON message(sender_id);

-- Ускоряет поиск непрочитанных сообщений
CREATE INDEX idx_message_is_read ON message(is_read);

-- Ускоряет проверку, подписан ли пользователь на канал
CREATE INDEX idx_subscription_user_channel ON subscription(user_id, channel_id);

-- Ускоряет выбор всех подписчиков канала
CREATE INDEX idx_subscription_channel_id ON subscription(channel_id);

-- Ускоряет выборку пользователей чата
CREATE INDEX idx_connect_chat_id ON connect(chat_id);
