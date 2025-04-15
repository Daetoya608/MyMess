from scripts import registration_process_console, load_settings, save_settings
from server_requests import register, login
from client_settings import ClientSettings
from client import Client
import asyncio

settings_data = load_settings()

if settings_data is None:
    while True:
        settings_data = registration_process_console()
        response = register(
            username=settings_data["username"],
            email=settings_data["email"],
            password=settings_data["password"],
            nickname=settings_data["nickname"]
        )
        if response["status"]:
            settings_data["id"] = response["id"]
            break

while True:
    settings_data["token"] = login(settings_data["username"], settings_data["password"])
    if settings_data["token"] is not None:
        break

save_settings(settings_data)

settings = ClientSettings()
settings.set_up_by_dict(settings_data)

client = Client(settings)

asyncio.run(client.websocket_client())
