from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str

class Product(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float

