import getpass
import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models.sephora import SephoraProductSQLModel

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Base.metadata.create_all(bind=engine)

def test_db_connection():
    try:
        # Create a session
        db = SessionLocal()
        
        # Retrieve the record
        result = db.query(SephoraProductSQLModel).first()
        print(f"Successfully connected to database and retrieved record: {result.product_name}")
        
        
        return True
    except Exception as e:
        print(f"Database connection test failed: {str(e)}")
        return False


# def test_qdrant():
#     try:
#         res = semantic_search("test")
#         print(res)
#     except Exception as e:
#         print(f"Qdrant connection test failed: {str(e)}")


# Test the database connection
print("Testing database connection...")
test_db_connection()

# print("Testing Qdrant connection...")
# test_qdrant()