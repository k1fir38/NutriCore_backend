from datetime import date
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Float, DATE, ForeignKey, CheckConstraint
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from .base import Base
from .enums import MealType
from ..calculators import calculate_macro_by_weight

if TYPE_CHECKING:
    from .user import User
    from .recipe import Recipe
    from .product import Product



class DiaryEntry(Base):
    __tablename__ = "diary_entries"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(DATE, nullable=False, index=True)
    meal_type: Mapped[MealType] = mapped_column(String, nullable=False)

    recipe_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=True)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    weight_grams: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped["User"] = relationship(back_populates="diary_entries")
    recipe: Mapped["Recipe"] = relationship(back_populates="diary")
    product: Mapped["Product"] = relationship(back_populates="diary")

    __table_args__ = (
        CheckConstraint(
            "(recipe_id IS NULL AND product_id IS NOT NULL) OR (recipe_id IS NOT NULL AND product_id IS NULL)",
            name="check_diary_entry_source"
        ),
    )

    @property
    def proteins_total(self) -> float:
        if self.product:
            return calculate_macro_by_weight(self.product.proteins, self.weight_grams)
        if self.recipe:
            return self.recipe.total_proteins
        return 0.0

    @property
    def fats_total(self) -> float:
        if self.product:
            return calculate_macro_by_weight(self.product.fats, self.weight_grams)
        if self.recipe:
            return self.recipe.total_fats
        return 0.0

    @property
    def carbs_total(self) -> float:
        if self.product:
            return calculate_macro_by_weight(self.product.carbs, self.weight_grams)
        if self.recipe:
            return self.recipe.total_carbs
        return 0.0

    @property
    def calories_total(self) -> float:
        if self.product:
            return (self.product.calories / 100) * self.weight_grams
        if self.recipe:
            return self.recipe.total_calories
        return 0.0