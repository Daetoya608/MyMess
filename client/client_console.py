from sqlalchemy.util import await_only

from scripts import registration_process_console, load_settings, save_settings
from server_requests import register, login
from client_settings import ClientSettings
from client import Client
from scripts import create_messages, create_chat
import asyncio
import websockets
from client_database import create_tables
from client_chats import ClientChats
import aiofiles


async def async_get_message_handler(messages: dict):
    messages_list: list = messages["messages"]
    # print("get_message_handler - begin")
    async with aiofiles.open("test_chat.txt", mode="a") as file:
        for message in messages_list:
            await file.write(message["content_text"] + "\n")


async def async_get_messages_handler_console(messages: dict, chat_obj: ClientChats = None, **kwargs):
    messages_list: list = messages["messages"]
    for message in messages_list:
        user_info = await chat_obj.get_from_users(message["sender_id"])
        print(f"{user_info['username']}: {message['content_text']}")


def get_message_handler(messages: dict, chat_obj: ClientChats = None, **kwargs):
    messages_list: list = messages["messages"]
    for message in messages_list:
        print(f"{message['sender_id']}: {message['content_text']}")


async def start():
    await create_tables()
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
                settings_data["id"] = response["user_id"]
                settings_data["username"] = response["username"]
                settings_data["email"] = response["email"]
                settings_data["nickname"] = response["nickname"]
                break

    while True:
        settings_data["token"] = login(settings_data["username"], settings_data["password"])
        if settings_data["token"] is not None:
            break

    save_settings(settings_data)

    settings = ClientSettings()
    settings.set_up_by_dict(settings_data)

    client = Client(settings)
    await client.chats.load_chats()
    return client


async def message_console(client):
    message = await asyncio.to_thread(input)
    if message[0] == "/":
        # print("message_console: begin")
        message_parts = message.split()
        if message_parts[0] == "/new_chat":
            # client.chats.select_chat(int(message_parts[1]))  # здесь проблема
            # print(f"messages_parts: {message_parts}")
            members_list = [int(message_parts[i]) for i in range(2, len(message_parts))]
            await client.server_request_create_chat(message_parts[1], members_list)
            return {
                "status": True,
                "is_command": True
            }
        elif message_parts[0] == "/change_chat":
            # print(f"messages_parts: {message_parts}")
            client.chats.select_chat(int(message_parts[1]))
            return {
                "status": True,
                "is_command": True
            }
    await client.add_to_sending_messages_queue(create_messages(message, client.chats.current_chat_id))
    return {"status": True}


async def message_console_task(client):
    while True:
        try:
            await message_console(client)
        except Exception as e:
            print(f"message_console_task - Exception: {e}")


async def websocket_client(domain = "127.0.0.1:8003"):
    client = await start()
    # client.get_message_handler_func = get_message_handler
    client.async_get_message_handler_func = async_get_messages_handler_console
    uri = f"ws://{domain}/ws"  # адрес твоего сервера
    async with websockets.connect(uri, additional_headers={"token": client.settings.token}) as websocket:
        task1 = asyncio.create_task(client.receiver_handler_task(websocket))
        task2 = asyncio.create_task(client.get_message_task(websocket))
        task3 = asyncio.create_task(client.send_message_task(websocket))
        task4 = asyncio.create_task(message_console_task(client))
        task5 = asyncio.create_task(client.execute_operation_task())
        task6 = asyncio.create_task(client.update_users_info_task())

        await task1
        await task2
        await task3
        await task4
        await task5
        await task6

asyncio.run(websocket_client())
