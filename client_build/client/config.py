import re
import os
import sys
from pathlib import Path
import appdirs

auth_url = None #"http://127.0.0.1:8001"
user_url = None #"http://127.0.0.1:8002"
chat_url = None #"http://127.0.0.1:8003"
chat_uri = None #"ws://127.0.0.1:8003"


APP_NAME = "MyMess"

def get_appdata_dir() -> Path:
    """Возвращает путь к директории данных приложения"""
    data_dir = Path(appdirs.user_data_dir(APP_NAME))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def resource_path(relative_path):
    """Возвращает корректный путь для ресурсов после сборки PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def create_new_file(file_path, text=""):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

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

    url_settings_path = get_appdata_dir() / "url_settings.txt"
    # url_settings_path = resource_path("url_settings.txt")
    print(f"\nURL_SETTINGS={url_settings_path}\n")
    result = {}
    # Чтение из файла
    if not os.path.exists(url_settings_path):
        print("NOT EXIST")
        create_new_file(url_settings_path)
        sys.exit()
    with open(url_settings_path, "r") as file:  # Укажите правильный путь к файлу!
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
