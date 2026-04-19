from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class IngredientCreate(BaseModel):
    product_id: int
    weight_grams: float

    model_config = ConfigDict(from_attributes=True)

class RecipeCreate(BaseModel):
    name: str
    instructions: Optional[str]
    ingredients: list[IngredientCreate] = Field(validation_alias="recipe_ingredients")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class RecipeRead(RecipeCreate):
    id: int