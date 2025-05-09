import getpass
import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.internal.qdrant import semantic_search

# load token from .env file
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Test model
class TestModel(Base):
    __tablename__ = "test_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

def test_db_connection():
    try:
        # Create a session
        db = SessionLocal()
        
        # Create a test record
        test_record = TestModel(name="test_record")
        db.add(test_record)
        db.commit()
        
        # Retrieve the record
        result = db.query(TestModel).first()
        print(f"Successfully connected to database and retrieved record: {result.name}")
        
        # Clean up
        db.delete(result)
        db.commit()
        db.close()
        
        return True
    except Exception as e:
        print(f"Database connection test failed: {str(e)}")
        return False


def test_qdrant():
    try:
        res = semantic_search("test")
        print(res)
    except Exception as e:
        print(f"Qdrant connection test failed: {str(e)}")


# Test the database connection
print("Testing database connection...")
test_db_connection()

print("Testing Qdrant connection...")
test_qdrant()