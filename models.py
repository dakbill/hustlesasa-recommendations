from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str
    name: str

class Product(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: float

