import requests

# URL вашего сервиса
BASE_URL = "http://localhost:8001"  # Укажите свой URL сервера

# Функция для регистрации пользователя
def register(username: str, password: str, email: str, nickname: str):
    url = f"{BASE_URL}/auth/register"  # Эндпоинт для регистрации
    data = {
        "username": username,
        "password": password,
        "email": email,  # Добавляем email
        "nickname": nickname,
    }

    response = requests.post(url, json=data)  # Отправляем POST-запрос с данными пользователя
    print(response.json())

# Функция для аутентификации пользователя
def login(username: str, password: str):
    url = f"{BASE_URL}/chat-service/sendMessage"  # Эндпоинт для аутентификации
    data = {
        "token": "asdsad",
        "password": password,
    }

    response = requests.post(url, json=data)  # Отправляем POST-запрос с логином и паролем
    # token = response.json()['access_token']
    # print(f"Access Token: {token}")
    # return token
    print(response.json())

# Пример использования
if __name__ == "__main__":
    username = "new_user_2053"
    password = "secepassword"
    email = "user2053@example.com"  # Добавляем email для регистрации
    nickname = "daetoyanaverno"

    # Регистрация
    register(username, password, email, nickname)

    # Аутентификация
    # token = login(username, password)

    # if token:
    #     print(f"Successfully logged in. Token: {token}")
