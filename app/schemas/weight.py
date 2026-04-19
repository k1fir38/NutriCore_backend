from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict
import datetime

class WeightCreate(BaseModel):
    weight_kilograms: float
    date: Optional[datetime.date] = None

    model_config = ConfigDict(from_attributes=True)


class WeightRead(BaseModel):
    id: int
    date: Optional[datetime.date] = None
    weight_kilograms: float

    model_config = ConfigDict(from_attributes=True)
