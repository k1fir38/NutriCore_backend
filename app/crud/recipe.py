from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, insert, ScalarResult, func, text, or_, and_

from app.core.models.recipe import Recipe, RecipeIngredient
from app.schemas.recipe import RecipeCreate, IngredientCreate


async def create_recipe(
        recipe_in: RecipeCreate,
        user_id: int,
        session: AsyncSession,

):

    db_recipe = Recipe(
        name=recipe_in.name,
        instructions=recipe_in.instructions,
        creator_id=user_id
    )
    session.add(db_recipe)
    await session.flush()

    for item in recipe_in.ingredients:
        db_ingredient = RecipeIngredient(
            recipe_id=db_recipe.id,
            product_id=item.product_id,
            weight_grams=item.weight_grams
        )
        session.add(db_ingredient)

    await session.commit()

    query = (
        select(Recipe)
        .where(Recipe.id == db_recipe.id)
        .options(
            joinedload(Recipe.recipe_ingredients)
            .joinedload(RecipeIngredient.product)  # Подгружаем продукт внутри ингредиента
        )
    )

    result = await session.execute(query)
    return result.unique().scalar_one()


async def find_all_recipes(session: AsyncSession, user_id: int) -> Sequence[Recipe]:

    query = (
        select(Recipe)
        .where(Recipe.creator_id == user_id)
        .options(
            joinedload(Recipe.recipe_ingredients)
            .joinedload(RecipeIngredient.product)
        )
    )

    result = await session.execute(query)

    return result.scalars().unique().all()

async def find_recipes_by_id(session: AsyncSession, user_id: int, recipe_id: int) -> Recipe | None:

    query = (
        select(Recipe)
        .where(
            and_(
                Recipe.creator_id == user_id,
                Recipe.id == recipe_id
            ))
        .options(
            joinedload(Recipe.recipe_ingredients)
            .joinedload(RecipeIngredient.product)
        )
    )

    result = await session.execute(query)

    return result.unique().scalar_one_or_none()

async def delete_recipe(
        session: AsyncSession,
        recipe_obj: Recipe
) -> None:
    await session.delete(recipe_obj)
    await session.commit()