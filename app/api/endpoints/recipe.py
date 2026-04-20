from fastapi import APIRouter, HTTPException, Depends, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.crud.recipe import create_recipe, find_all_recipes, find_recipes_by_id, delete_recipe
from app.db.session import get_async_session
from app.schemas.recipe import RecipeRead, RecipeCreate

router = APIRouter(tags=["recipe"], prefix="/recipe")

@router.post("/", response_model=RecipeRead)
async def create_new_recipe(
    recipe_in: RecipeCreate,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    recipe = await create_recipe(
        recipe_in=recipe_in,
        user_id=current_user.id,
        session=session
    )
    return recipe

@router.get("/", response_model=list[RecipeRead])
async def get_recipes(
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):

    recipes = await find_all_recipes(
        session=session,
        user_id=current_user.id
    )

    if recipes is None:
        raise HTTPException(
            status_code=404,
            detail="Recipes not found"
        )
    return recipes

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipes(
    recipe_id: int,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):

    recipe = await find_recipes_by_id(
        session=session,
        user_id=current_user.id,
        recipe_id=recipe_id
    )

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipes not found"
        )

    await delete_recipe(session=session,recipe_obj=recipe)

@router.post("/{recipe_id}", response_model=RecipeRead)
async def create_new_recipe(
        recipe_id: int,
        current_user=Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    recipe = await find_recipes_by_id(
        recipe_id=recipe_id,
        user_id=current_user.id,
        session=session
    )
    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )
    return recipe