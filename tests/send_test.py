import requests

# URL вашего сервиса
BASE_URL = "http://localhost:8002"  # Укажите свой URL сервера


def test_send(token, sender, receiver, content):
    url = f"{BASE_URL}/chat-service/sendMessage"  # Эндпоинт для регистрации
    data = {
        "token": token,
        "sender_id": sender,
        "receiver_id": receiver,
        "content": content,
    }

    response = requests.post(url, json=data)  # Отправляем POST-запрос с данными пользователя
    print(response.json())



if __name__ == "__main__":
    token = "nsadsajd3"
    sender = 1
    receiver = 1
    content = {
        "text_content": "hello world"
    }

    test_send(token, sender, receiver, content)

