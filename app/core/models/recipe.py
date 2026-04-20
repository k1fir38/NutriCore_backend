from datetime import date
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Float, DATE, ForeignKey, Text, Null
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from .base import Base
from .enums import UnitName

if TYPE_CHECKING:
    from .user import User
    from .diary import DiaryEntry
    from .product import Product



class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    creator: Mapped["User"] = relationship(back_populates="recipes")
    diary: Mapped["DiaryEntry"] = relationship(back_populates="recipe",
                                               cascade="all, delete-orphan",
                                               passive_deletes=True
                                               )
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    @property
    def total_weight(self):
        return sum(item.weight_grams for item in self.recipe_ingredients)

    @property
    def total_calories(self):
        total = 0
        for item in self.recipe_ingredients:
            total += (item.product.calories / 100) * item.weight_grams
        return total

    @property
    def calories_per_100g(self):
        if self.total_weight == 0:
            return 0.0
        return (self.total_calories / self.total_weight) * 100

    @property
    def total_proteins(self):
        total = 0
        for item in self.recipe_ingredients:
            total += (item.product.proteins / 100) * item.weight_grams
        return total

    @property
    def total_fats(self):
        total = 0
        for item in self.recipe_ingredients:
            total += (item.product.fats / 100) * item.weight_grams
        return total

    @property
    def total_carbs(self):
        total = 0
        for item in self.recipe_ingredients:
            total += (item.product.carbs / 100) * item.weight_grams
        return total

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    weight_grams: Mapped[float] = mapped_column(Float, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="recipe_ingredients")
    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")