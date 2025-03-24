import websockets
import asyncio

async def client():
    async with websockets.connect("ws://127.0.0.1:8000/ws") as ws:
        await ws.send("Привет!")
        response = await ws.recv()
        print(f"Ответ: {response}")
        input()


asyncio.run(client())
