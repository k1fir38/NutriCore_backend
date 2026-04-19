from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, Response, Cookie

from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.user import UserRead, UserCreate, UserLogin
from app.db.session import get_async_session
from app.crud.user import get_user_by_email, create_user
from app.core.security import PasswordHelper


router = APIRouter(tags=["Auth"], prefix="/auth")

@router.post("/register", response_model=UserRead)
async def register(
        user_in: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):

    user = await get_user_by_email(session=session, email=user_in.email)

    if user is not None:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = await create_user(session=session, user_in=user_in)

    return user


@router.post("/login", response_model=UserRead)
async def login(
        response: Response,
        data_user: UserLogin,
        session: AsyncSession = Depends(get_async_session)
):
    user = await get_user_by_email(session=session, email=data_user.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not PasswordHelper.verify_password(
            plain_password=data_user.password,
            hashed_password=user.hashed_password
    ):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    access_token = PasswordHelper.create_access_token(
        {
            "sub": str(user.id),
            "type": "access"
        }
    )
    refresh_token = PasswordHelper.create_access_token(
        {
            "sub": str(user.id),
            "type": "refresh"
        },
        expires_delta=timedelta(days=7)
    )

    response.set_cookie("access_token", access_token, httponly=True, max_age=1800)
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=3600*24*7)
    return user

@router.post("/refresh")
async def process_refresh_token(
        response: Response,
        refresh_token: str | None = Cookie(None)
):

    payload = PasswordHelper.decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token required")

    user_id = payload.get("sub")

    access_token = PasswordHelper.create_access_token(
        {
            "sub": str(user_id),
            "type": "access"
        }
    )

    response.set_cookie("access_token", access_token, httponly=True, max_age=1800)

    return {"detail": "Refresh successful"}


@router.post("/logout")
async def logout(
        response: Response,
):
    response.delete_cookie("access_token", httponly=True)
    response.delete_cookie("refresh_token", httponly=True)

    return {"detail": "Successfully logged out"}