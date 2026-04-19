

from fastapi import APIRouter, HTTPException, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.schemas.product import ProductRead, ProductCreate
from app.db.session import get_async_session
from app.crud.product import (
        find_all_product,
        find_by_name_product,
        create_custom_product,
        find_by_id_product,
        delete_custom_product,

    )

router = APIRouter(tags=["product"], prefix="/product")

@router.get(path="/", response_model=list[ProductRead])
async def get_products(
        session: AsyncSession = Depends(get_async_session)
):
    products = await find_all_product(session=session)

    if products is None:
        raise HTTPException(
            status_code=404,
            detail="Products not found"
        )
    return products


@router.get("/search", response_model=list[ProductRead])
async def search_products(
        name: str,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):

    products = await find_by_name_product(
        session=session,
        product_name=name,
        user_id=current_user.id
    )

    if not products:
        raise HTTPException(status_code=404, detail="Products not found")

    return products

@router.post("/me", response_model=ProductRead)
async def create_product(
        product_in: ProductCreate,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):

    user_id = current_user.id

    new_product = await create_custom_product(
        session=session,
        product_in=product_in,
        user_id=user_id
    )

    if not new_product:
        raise HTTPException(
            status_code=400,
            detail="Bad request"
        )

    return new_product


@router.delete("/me/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
        product_id: int,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    product = await find_by_id_product(session=session, product_id=product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Not found"
        )

    if current_user.id != product.creator_id:
        raise HTTPException(
            status_code=403,
            detail="Access to the requested resource is denied"
        )
    await delete_custom_product(session=session, product_obj=product)

    return None




