import re
import os


auth_url = None #"http://127.0.0.1:8001"
user_url = None #"http://127.0.0.1:8002"
chat_url = None #"http://127.0.0.1:8003"
chat_uri = None #"ws://127.0.0.1:8003"


def load_url_info():
    global auth_url, user_url, chat_url, chat_uri
    pattern = r"""
        ^\s*                              
        (auth_url|user_url|chat_url)      
        \s*=\s*                           
        \{                                
        ([^{}]*)                          
        \}                                
        \s*$                              
    """

    result = {}
    # Чтение из файла
    if not os.path.exists("url_settings.txt"):
        print("NOT EXIST")
        return
    with open("url_settings.txt", "r") as file:  # Укажите правильный путь к файлу!
        for line in file:  # Читаем файл построчно
            match = re.search(pattern, line, re.VERBOSE)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                result[key] = value

    auth_url = result["auth_url"]
    user_url=result["user_url"]
    chat_url=result["chat_url"]
    chat_uri="wss" + result["chat_url"][5:]
