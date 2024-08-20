from sqlalchemy.orm import Session
import models, schemas

# Create a product
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(name=product.name, link=product.link)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Get a list of products with pagination
def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Product).offset(skip).limit(limit).all()

# Get a single product by ID
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

# Search products by name (simple search)
def search_products(db: Session, query: str):
    return db.query(models.Product).filter(models.Product.name.ilike(f"%{query}%")).all()

# Delete a product by ID
def delete_product(db: Session, product_id: int):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return db_product
    return None

# Delete all products
def delete_all_products(db: Session):
    deleted_count = db.query(models.Product).delete()
    db.commit()
    return deleted_count

