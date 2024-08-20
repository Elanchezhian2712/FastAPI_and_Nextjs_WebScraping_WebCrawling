from pydantic import BaseModel

# Product schema for reading
class ProductBase(BaseModel):
    name: str
    link: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True  