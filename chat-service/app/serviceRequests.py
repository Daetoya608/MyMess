from typing import List, Dict
import httpx

host = "127.0.0.1:8002"


async def get_users_info(users_ids: List[int]) -> Dict:
    '''
    :param users_ids:
    :return: {
        "status": bool,
        "users_data": list[dict] = [
            {
                "user_id": int,
                "username": str,
                "nickname": str,
            }
        ]
    }
    '''

    request_data = {
        "users_ids": users_ids
    }
    answer = dict()
    url = "http://{host}/user-service/info"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=request_data)
        if 200 <= response.status_code < 300:
            answer = response.json()
            answer["status"] = True
            return answer
    answer["status"] = False
    return answer


