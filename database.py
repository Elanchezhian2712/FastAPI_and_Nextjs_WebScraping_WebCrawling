from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse


password = '12345'

encoded_password = urllib.parse.quote_plus(password)

SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{encoded_password}@localhost:5432/web"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()