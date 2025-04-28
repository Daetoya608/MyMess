import requests
from typing import Dict

# DOMAIN_HTTP = "https://called-hear-cds-neighborhood.trycloudflare.com"
DOMAIN_HTTP = input("Введи url auth сервиса: ")


def register(username: str, password: str, email: str, nickname: str):
    """return {
        "id": int,
        "status": bool
    }"""
    url = f"{DOMAIN_HTTP}/auth-service/register"  # Эндпоинт для регистрации
    data = {
        "username": username,
        "password": password,
        "email": email,  # Добавляем email
        "nickname": nickname,
    }

    response = requests.post(url, json=data)  # Отправляем POST-запрос с данными пользователя
    # print(response.json())
    # print(response.status_code)
    response_data: Dict = response.json()
    response_data["status"] = True if 200 <= response.status_code < 300 else False
    return response_data


def login(username: str, password: str) -> str:
    """"return token: str"""

    url = f"{DOMAIN_HTTP}/auth-service/login"  # Эндпоинт для аутентификации
    data = {
        "username":  username,
        "password": password
    }

    response = requests.post(url, json=data)  # Отправляем POST-запрос с логином и паролем
    token = response.json()['access_token']
    # print(f"Access Token: {token}")
    print(response.json())
    return token
