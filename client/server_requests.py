import requests
from typing import Dict

from .config import auth_url, user_url

# DOMAIN_HTTP = "https://called-hear-cds-neighborhood.trycloudflare.com"
# DOMAIN_HTTP = input("Введи url auth сервиса: ")
# DOMAIN_HTTP1 = "http://127.0.0.1:8001"
# DOMAIN_HTTP2 = "http://127.0.0.1:8002"

def register(username: str, password: str, email: str, nickname: str):
    """return {
        "id": int,
        "status": bool
    }"""
    url = f"{auth_url}/auth-service/register"  # Эндпоинт для регистрации
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


def login(username: str, password: str) -> dict:
    url = f"{auth_url}/auth-service/login"  # Эндпоинт для аутентификации
    data = {
        "username":  username,
        "password": password
    }

    response = requests.post(url, json=data)  # Отправляем POST-запрос с логином и паролем
    # token = response.json()['access_token']
    # print(f"Access Token: {token}")
    response_data = response.json()
    response_data["status"] = True if 200 <= response.status_code < 300 else False
    print(response_data)
    return response_data


def get_user_by_username(username: str):
    url = f"{user_url}/user-service/user_id/{username}"
    response = requests.get(url)
    response_data = response.json()
    response_data["status"] = True if 200 <= response.status_code < 300 else False
    print(response_data)
    return response_data

