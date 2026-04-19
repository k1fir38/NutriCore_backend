from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request, HTTPException, Cookie
from jose import JWTError, jwt

from app.core.config import settings
from app.core.models.user import User
from app.core.security import PasswordHelper
from app.crud.user import get_user_by_id
from app.db.session import get_async_session


async def get_token(
        access_token: str | None = Cookie(None)
) -> str:
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authorized")
    return access_token


async def get_current_user(
        session: AsyncSession = Depends(get_async_session),
        token: str = Depends(get_token)) -> User | None:

    try:
        payload = PasswordHelper.decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Access token required")


    expire: Any = payload.get("exp")
    if not expire or (int(expire) < datetime.now(timezone.utc).timestamp()):
        raise HTTPException(
            status_code=401,
            detail="Token lifetime has expired"
        )

    user_id: Any = int(payload.get("sub"))
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail=""
        )

    user = await get_user_by_id(session=session, id=user_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Token type is invalid"
        )

    return user


