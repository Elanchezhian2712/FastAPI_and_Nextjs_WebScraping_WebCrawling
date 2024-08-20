from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.common.exceptions import NoSuchElementException

# Create the database tables
models.Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI()

# CORS Middleware
origins = [
    "http://localhost:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Chrome WebDriver with custom options
def get_driver():
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode (no UI)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Scraping function
def scrape_amazon(search_query: str, max_pages: int = 3):
    driver = get_driver()
    all_products = []
    
    try:
        page_number = 1
        while page_number <= max_pages:
            amazon_url = f"https://www.amazon.com/s?k={search_query.replace(' ', '+')}&i=stripbooks-intl-ship&page={page_number}"
            driver.get(amazon_url)
            time.sleep(5)
            products = driver.find_elements(By.CSS_SELECTOR, "h2 a")
            
            if not products:
                print(f"No products found on page {page_number}.")
                break
            
            for product in products:
                try:
                    product_link = product.get_attribute('href')
                    product_name = product.text.strip()
                    
                    if product_name:
                        print(f"Scraped product: {product_name}, Link: {product_link}")
                        all_products.append((product_name, product_link))
                    else:
                        print("Found a product with no name.")
                    
                except Exception as e:
                    print(f"Error retrieving product: {e}")
            
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "ul.a-pagination li.a-last a")
                if next_button:
                    next_button.click()
                    time.sleep(5)
                else:
                    break
            except NoSuchElementException:
                break
            
            page_number += 1
    
    finally:
        driver.quit()
    
    return all_products

@app.post("/search_and_store/{search_query}", response_model=list[schemas.Product])
def search_and_store_products(search_query: str, max_pages: int = 3, db: Session = Depends(get_db)):
    products = scrape_amazon(search_query, max_pages)
    saved_products = []
    
    for name, link in products:
        if name:
            product = schemas.ProductCreate(name=name, link=link)
            try:
                saved_product = crud.create_product(db=db, product=product)
                saved_products.append(saved_product)
            except Exception as e:
                print(f"Error saving product {name}: {e}")
    
    return saved_products

@app.get("/products/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = crud.get_products(db=db, skip=skip, limit=limit)
    return products

@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.get("/search/", response_model=list[schemas.Product])
def search_product(query: str, db: Session = Depends(get_db)):
    products = crud.search_products(db=db, query=query)
    return products

@app.delete("/products/{product_id}", response_model=schemas.Product)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted_product = crud.delete_product(db=db, product_id=product_id)
    if deleted_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted_product

@app.delete("/products/", response_model=int)
def delete_all_products(db: Session = Depends(get_db)):
    try:
        deleted_count = crud.delete_all_products(db=db)
        return deleted_count
    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail="An error occurred while deleting all products.")
