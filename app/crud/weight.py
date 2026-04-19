from datetime import date
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, insert, ScalarResult, func, text, or_, and_
from sqlalchemy.sql.functions import current_user

from app.core.models import User
from app.schemas.weight import WeightCreate
from app.core.models.weight_history import WeightHistory



async def record_user_weight(
        session: AsyncSession,
        weight_in: WeightCreate,
        user_id: int
):
    date_today = date.today()

    if weight_in.date == None:
        weight_in.date = date_today

    query = select(WeightHistory).where(
        and_(
            WeightHistory.user_id == user_id,
            WeightHistory.date == weight_in.date

        )
    )
    result = await session.execute(query)
    w_history = result.scalar_one_or_none()

    if w_history is None:
        w_history = WeightHistory(
            user_id=user_id,
            date=weight_in.date,
            weight_kilograms=weight_in.weight_kilograms
        )
        session.add(w_history)
    else:
        w_history.weight_kilograms = weight_in.weight_kilograms
        session.add(w_history)

    user = await session.get(User, user_id)
    user.weight = weight_in.weight_kilograms

    await session.commit()
    await session.refresh(w_history)
    return w_history

async def find_all_weights(
        session: AsyncSession,
        user_id: int

) -> Sequence[WeightHistory]:

    query = select(WeightHistory).where(WeightHistory.user_id == user_id)
    weights = await session.execute(query)
    return weights.scalars().all()

async def find_weight_by_id(
        session: AsyncSession,
        weight_id: int

) -> WeightHistory | None:

    query = select(WeightHistory).where(WeightHistory.id == weight_id)
    weight = await session.execute(query)
    return weight.scalar_one_or_none()

async def delete_weight(
        session: AsyncSession,
        weight_obj: WeightHistory
) -> None:

    user_id = weight_obj.user_id
    await session.delete(weight_obj)

    query = (
        select(WeightHistory)
        .where(WeightHistory.user_id == user_id)
        .order_by(WeightHistory.date.desc())
        .limit(1)
    )
    result = await session.execute(query)
    new_latest_record = result.scalar_one_or_none()

    user = await session.get(User, user_id)

    if user:
        if new_latest_record:
            user.weight = new_latest_record.weight_kilograms
        else:

            user.weight = 0.0

    await session.commit()