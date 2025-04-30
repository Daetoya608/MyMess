from typing import List

def create_chat_request(chat_name: str, members: List[str]):
    data = {
        "type": "create_chat",
        "chat_data": {
            "chat_name": chat_name,
            "members": members
        }
    }
    return data
