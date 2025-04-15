import asyncio
import websockets
import json
import time

def create_messages(text_message: str, sender_id: int, chat_id: int):
    request_data = {
        "type": "messages",
        "time_key": time.perf_counter_ns(),
        "messages": [
            {
                "sender_id": sender_id,
                "chat_id": chat_id,
                "content_text": text_message
            },
        ]
    }
    return request_data


async def send_ask(websocket: websockets.ClientConnection, time_key: int):
    try:
        requests_data = {
            "type": "ack",
            "time_key": time_key
        }
        requests_data_json = json.dumps(requests_data)
        await websocket.send(requests_data_json)
    except Exception as e:
        print(f"send_ask - Exception: {e}")

# async def get_mode(uri, token):
#     async with websockets.connect(uri, additional_headers={"token": token}) as websocket:
#         while True:
#             response_data = await websocket.recv()
#             response_data_dict = json.loads(response_data)
#             data = json.loads(response_data_dict)
#             print(f"ТИП - {type(data)}")
#             print(data)
#             print(type(data["time_key"]))
#             await send_ask(websocket, int(data["time_key"]))
#             await asyncio.sleep(1)
#             break
#
#
# async def send_mode(uri, token):
#     async with websockets.connect(uri, additional_headers={"token": token}) as websocket:
#         while True:
#             message = await asyncio.to_thread(input, "Введи сообщение: ") #input("Write message: ")
#             await websocket.send(json.dumps(create_messages(message, 1, 1)))
#             print("Отправлено")
#             response = await websocket.recv()
#             print(f"Получено от сервера: {response}")
#             await asyncio.sleep(1)
#             break


messages_queue = asyncio.Queue()
ack_queue = asyncio.Queue()

def default_answer(time_key):
    answer: dict = {
        "type": "ack",
        "time_key": time_key
    }
    return answer

async def send_data(websocket: websockets.ClientConnection, data: dict):
    await websocket.send(json.dumps(data))

async def receiver_handler(websocket: websockets.ClientConnection):
    request_str: str = await websocket.recv()
    request_data: dict = json.loads(json.loads(request_str))
    if request_data.get("type") == "messages":
        await messages_queue.put(request_data)
        await send_data(websocket, default_answer(request_data.get("time_key")))

        await asyncio.sleep(0.1)
    elif request_data.get("type") == "ack":
        await ack_queue.put(request_data)
    else:
        print("Неверная структура данных")

async def receiver_handler_task(websocket: websockets.ClientConnection):
    while True:
        try:
            await receiver_handler(websocket)
        except Exception as e:
            print(f"receiver_handler_task - Exception: {e}")
            continue

result_list = []

async def get_message(websocket: websockets.ClientConnection):
        data: dict = await messages_queue.get()
        result_list.append(data)
        print(f"\ndata-get_message: {data}\n")
        await send_ask(websocket, int(data["time_key"]))
        await asyncio.sleep(0.1)


async def get_message_task(websocket: websockets.ClientConnection):
    while True:
        try:
            await get_message(websocket)
        except Exception as e:
            print(f"get_message_task - Exception: {e}")
            continue


async def send_message(websocket: websockets.ClientConnection, sender_id):
    message = await asyncio.to_thread(input)  # input("Write message: ")

    if message == "result":
        print(f"COUNT: {len(result_list)}\n\ndata={result_list}")
        return True

    await websocket.send(json.dumps(create_messages(message, sender_id, 1)))
    print("Отправлено")
    response = await ack_queue.get()
    print(f"Получено от сервера, ack: {response}")
    await asyncio.sleep(0.1)

async def send_message_task(websocket: websockets.ClientConnection, sender_id):
    while True:
        try:
            await send_message(websocket, sender_id)
        except Exception as e:
            print(f"send_message_task - Exception: {e}")
            continue


async def websocket_client():
    domain = input("Введите сайт: ")
    uri = f"wss://{domain}/ws"  # адрес твоего сервера
    id = int(input("Введи id: "))
    token = input("Введите токен: ")


    async with websockets.connect(uri, additional_headers={"token": token}) as websocket:
        task1 = asyncio.create_task(receiver_handler_task(websocket))
        task2 = asyncio.create_task(get_message_task(websocket))
        task3 = asyncio.create_task(send_message_task(websocket, id))

        await task1
        await task2
        await task3

asyncio.run(websocket_client())
