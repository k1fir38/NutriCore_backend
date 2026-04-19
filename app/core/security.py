

import bcrypt
from fastapi import HTTPException

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

class PasswordHelper:

    @staticmethod
    def hash_password(password: str) -> str:
        """Превращает пароль в защищенный хеш"""
        pw_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(pw_bytes, salt)
        return hashed_pw.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет, совпадает ли введенный пароль с хешем из базы"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        if expires_delta is not None:
            expire = datetime.now(timezone.utc) + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str | None) -> dict:  # Возвращаем словарь
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            # Прямо здесь кидаем ошибку, чтобы не дублировать это в роутерах
            raise HTTPException(status_code=401, detail="Token invalid or expired")