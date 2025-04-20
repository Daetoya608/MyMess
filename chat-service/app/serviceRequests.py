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
            },
        ]
    }
    '''
    users_ids_str = ",".join(map(str, users_ids))
    request_data = {
        "users_ids": users_ids_str
    }
    print(f"get_users_info - begin\nuser_ids_str = {users_ids_str}")
    answer = dict()
    url = f"http://{host}/user-service/info"
    async with httpx.AsyncClient() as client:
        print(f"get_users_info - client.begin")
        response = await client.get(url, params=request_data)
        print(f"get_users_info - status_code = {response.status_code}")
        if 200 <= response.status_code < 300:
            answer = response.json()
            answer["status"] = True
            return answer
    answer["status"] = False
    return answer


