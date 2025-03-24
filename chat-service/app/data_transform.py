from fastapi import WebSocket
from chat import decode_jwt


def get_data_from_websocket_header(websocket: WebSocket):
    return websocket.headers

def get_token_from_websocket_header(websocket: WebSocket):
    return websocket.headers.get("token")

def get_token_data_from_websocket(websocket: WebSocket):
    token = get_token_from_websocket_header(websocket)
    if token is None:
        return None
    return decode_jwt(token)

def get_id_from_websocket(data_from_websocket: dict):
    return data_from_websocket["id"]

def get_username_from_websocket(data_from_websocket: dict):
    return data_from_websocket["username"]

def get_token_from_websocket(data_from_websocket: dict):
    return data_from_websocket["token"]
