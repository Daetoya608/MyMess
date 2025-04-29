import json
from typing import Dict, List
import os.path
import time
from .server_requests import register

def create_messages(text_message: str, chat_id: int):
    request_data = {
        "type": "messages",
        "time_key": time.perf_counter_ns(),
        "messages": [
            {
                "chat_id": chat_id,
                "content_text": text_message
            },
        ]
    }
    return request_data


def create_chat(chat_name: str, members_list: List[int]):
    request_data = {
        "type": "commands",
        "time": time.perf_counter_ns(),
        "commands": [
            {
                "command": "create_chat",
                "chat_name": chat_name,
                "members": members_list,
            },
        ]
    }
    return request_data


def create_chat_by_usernames(chat_name: str, member_usernames: List[str]):
    request_data = {
        "type": "commands",
        "time": time.perf_counter_ns(),
        "commands": [
            {
                "command": "create_chat_by_usernames",
                "chat_name": chat_name,
                "members": member_usernames,
            },
        ]
    }
    return request_data


def default_answer(time_key):
    answer: dict = {
        "type": "ack",
        "time_key": time_key
    }
    return answer


def default_func(*args, **kwargs):
    return


async def async_default_func(*args, **kwargs):
    return


def save_settings(settings: Dict):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


def load_settings():
    if not os.path.exists("settings.json"):
        return None
    with open("settings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def is_reg():
    return os.path.exists("settings.json")


def update_settings(new_data: dict):
    data = load_settings()
    if data is None:
        data = dict()
    for key in new_data:
        data[key] = new_data[key]
    save_settings(data)
    return data

def registration_process_console() -> Dict[str, str]:
    """return {"username": str, "email": str, "password": str, "nickname": str}"""

    user_settings = dict()
    print("--------Регистрация--------")
    user_settings["email"] = input("Введите email: ")
    user_settings["username"] = input("Введите username: ")
    user_settings["password"] = input("Введите пароль: ")
    user_settings["nickname"] = input("Введите ник: ")
    print("---------------------------")
    return user_settings


def server_registration_process(registration_process_func=registration_process_console):
    is_server_reg = False
    while not is_server_reg:
        data: Dict[str, str] = registration_process_func()
        is_server_reg = register(
            username=data["username"],
            password=data["password"],
            email=data["email"],
            nickname=data["nickname"]
        )
    return True


