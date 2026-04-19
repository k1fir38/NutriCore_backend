from fastapi import APIRouter, HTTPException, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_async_session
from app.schemas.weight import WeightRead, WeightCreate
from app.crud.weight import find_all_weights, record_user_weight, find_weight_by_id, delete_weight

router = APIRouter(tags=["weight"], prefix="/weight")

@router.get("/history", response_model=list[WeightRead])
async def get_weight(
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):

    weights = await find_all_weights(
        session=session,
        user_id=current_user.id
    )

    if weights is None:
        raise HTTPException(
            status_code=404,
            detail="Weights not found"
        )
    return weights

@router.post("/", response_model=WeightRead)
async def create_weight(
        weight_in: WeightCreate,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):

    weight = await record_user_weight(
        session=session,
        weight_in=weight_in,
        user_id=current_user.id
    )

    if weight is None:
        raise HTTPException(
            status_code=404,
            detail="Bad request"
        )
    return weight


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weight_user(
        weight_id: int,
        current_user = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):

    weight = await find_weight_by_id(
        session=session,
        weight_id=weight_id
    )

    if weight is None:
        raise HTTPException(
            status_code=404,
            detail="Weight not found"
        )

    if current_user.id != weight.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access to the requested resource is denied"
        )
    await delete_weight(session=session, weight_obj=weight)

    return None
