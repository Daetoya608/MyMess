from scripts import is_reg, load_settings, save_settings
from typing import Dict

class ClientSettings:

    def __init__(self):
        self.username = None
        self.password = None
        self.email = None
        self.nickname = None
        self.id = None
        self.token = None


    def set_up_by_dict(self, user_settings_data: Dict):
        """user_settings_data = {
            "username": str,
            "email": str,
            "password": str,
            "nickname": str,
            "id": int,
            "token": str
        }"""
        self.username = user_settings_data["username"]
        self.email = user_settings_data["email"]
        self.password = user_settings_data["password"]
        self.nickname = user_settings_data["nickname"]
        self.id = user_settings_data["id"]
        self.token = user_settings_data["token"]

        save_settings(user_settings_data)


    def set_up(self, username, email, password, nickname, id, token):
        self.username = username
        self.email = email
        self.password = password
        self.nickname = nickname
        self.id = id
        self.token = token

        save_settings({
            "username": username,
            "email": email,
            "password": password,
            "nickname": nickname,
            "id": id,
            "token": token
        })
