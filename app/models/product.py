from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
