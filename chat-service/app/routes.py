
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from schemas import SendRequest, MessageResponse
from models import add_message, add_content, Message, get_unread_messages_for_user
from chat import decode_jwt

router = APIRouter()


@router.post("/sendMessage")
async def send_message(data: SendRequest):
    # need: проверка прав токена
    content_id = await add_content(data.content.text_content)
    if content_id <= 0:
        raise HTTPException(
            status_code=500,
            detail="something went wrong. Try again later"
        )
    message_id = await add_message(
        sender_id=data.sender_id,
        receiver_id=data.receiver_id,
        content_id=content_id
    )
    if message_id <= 0:
        raise HTTPException(
            status_code=500,
            detail="something went wrong. Try again later"
        )
    return JSONResponse(
        status_code=200,
        content={
            "description": "Сообщение доставлено"
        }
    )


@router.get("/unread")
async def get_unread_messages(request: Request):
    token = dict(request.headers)["token"]
    data = decode_jwt(token)
    if not data:
        raise HTTPException(status_code=400,
                            detail="invalid token")
    # !!!!Проверка токена
    user_id = data["user_id"]
    messages = await get_unread_messages_for_user(user_id)
    MessageResponse.model_validate(messages[0])