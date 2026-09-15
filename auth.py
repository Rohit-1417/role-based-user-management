from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import datetime, timedelta, timezone
import string
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context=CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password:str):
    return pwd_context.hash(password)


def verify_password(password:str,hashed_password:str):
    return pwd_context.verify(password,hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_token(token: str):
    try:
        payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

        return payload

    except JWTError:
        return None



def create_reset_token(user_id: int):
    to_encode = {
        "user_id": user_id,
        "type": "password_reset"
    }

    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token




def generate_temporary_password(length=12):
    letters = string.ascii_letters
    digits = string.digits
    symbols = "!@#$%^&*"

    password = (
        secrets.choice(letters)
        + secrets.choice(digits)
        + secrets.choice(symbols)
    )

    all_characters = letters + digits + symbols

    for _ in range(length - 3):
        password += secrets.choice(all_characters)

    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)

    return "".join(password_list)



def create_first_login_token(user_id: int):
    to_encode = {
        "user_id": user_id,
        "type": "first_login"
    }

    expire = datetime.now(timezone.utc) + timedelta(minutes=10)

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token