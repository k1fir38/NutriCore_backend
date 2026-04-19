from datetime import date
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, insert, ScalarResult

from app.core.models import Recipe, RecipeIngredient
from app.schemas.diary import DiaryEntryCreate
from app.core.security import PasswordHelper
from app.core.models.diary import DiaryEntry



async def create_diary_entry(
        session: AsyncSession,
        diary_in: DiaryEntryCreate,
        user_id: int,
) -> DiaryEntry:

    # Превращаем схему в словарь и добавляем user_id
    diary_data = diary_in.model_dump()
    diary = DiaryEntry(
        **diary_data,
        user_id=user_id
    )

    session.add(diary)
    await session.commit()
    await session.refresh(diary)

    return diary


async def get_user_diary_for_date(session: AsyncSession, user_id: int, diary_date: date):
    query = (
        select(DiaryEntry)
        .where(DiaryEntry.user_id == user_id)
        .where(DiaryEntry.date == diary_date)
        .options(
            joinedload(DiaryEntry.product),
            joinedload(DiaryEntry.recipe)
            .joinedload(Recipe.recipe_ingredients)
            .joinedload(RecipeIngredient.product)
        )
    )

    result = await session.execute(query)
    return result.scalars().unique().all()

async def delete_diary_entry(session: AsyncSession, diary_obj: DiaryEntry) -> None:
    """Принимает готовый объект и удаляет его"""
    await session.delete(diary_obj)
    await session.commit()


async def find_dairy_by_id(
        session: AsyncSession,
        dairy_id: int,
) -> DiaryEntry | None:
    query = (
        select(DiaryEntry)
        .where(DiaryEntry.id == dairy_id)
    )

    result = await session.execute(query)
    return result.scalar_one_or_none()

async def update_diary(session: AsyncSession, diary) -> DiaryEntry | None:
    session.add(diary)
    await session.commit()
    await session.refresh(diary, ["product"])

    return diary