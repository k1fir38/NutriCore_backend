from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, insert, ScalarResult, func, text, or_, and_

from app.core.models.product import Product
from app.schemas.product import ProductCreate



async def find_all_product(session: AsyncSession) -> Sequence[Product]:

    query = (
        select(Product)
    )

    result = await session.execute(query)

    return result.scalars().all()

async def find_by_id_product(session: AsyncSession, product_id: int) -> Product | None:

    query = (
        select(Product)
        .where(Product.id == product_id)
    )

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def find_by_name_product(
        session: AsyncSession,
        product_name: str,
        user_id: int,
) -> Sequence[Product]:
    """
    query = (
        select(Product)
        .where(Product.name.ilike(f"%{product_name}%"))
        .limit(limit)   # применяем лимит
        .offset(offset) # применяем смещение
    )
    """
    # await session.execute(text("SET LOCAL pg_trgm.similarity_threshold = 0.2"))


    query = (
        select(Product)
        .where(
            and_(
                (Product.name.op('%')(product_name)),
                or_(
                    (Product.creator_id == None),
                    (Product.creator_id == user_id)
                )
            )


        )
        .order_by(func.similarity(Product.name, product_name).desc())  # Самые похожие — первыми
    )
    result = await session.execute(query)
    return result.scalars().all()


async def create_custom_product(
        session: AsyncSession,
        product_in: ProductCreate,
        user_id: int,
) -> Product:

    product_data = product_in.model_dump()

    product = Product(
        **product_data,
        creator_id=user_id
    )

    session.add(product)
    await session.commit()
    await session.refresh(product)

    return product

async def delete_custom_product(
        session: AsyncSession,
        product_obj: Product
) -> None:
        await session.delete(product_obj)
        await session.commit()