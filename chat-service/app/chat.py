from datetime import timedelta, datetime, UTC

from passlib.context import CryptContext
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return context.hash(password)

def check_hash_and_password(input_password: str, password_hash: str) -> bool:
    return context.verify(input_password, password_hash)

def create_jwt(payload: dict, lifetime: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data = payload.copy()
    expire = datetime.now(UTC) + lifetime
    data.update({"exp": expire})
    return jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


print(create_jwt(
    payload={
        "id": 5,
        "username": "forexample"
    }
))
print(decode_jwt("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwidXNlcm5hbWUiOiJmb3JleGFtcGxlIiwiZXhwIjoxNzQzODAyMjIyfQ.QlyFkcIwBVM0glSFhgP-HOZZrfK7kbL-b8DOPjKGik0"))
