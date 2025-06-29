import os
import sys

# Add the project root to Python path (go up 2 levels from dataV2/2_qdrant/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import uuid
from app.internal.embedding_v2 import create_review_embedding, create_product_embedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import psycopg2
from dotenv import load_dotenv

def create_database_connection(db_url):
    """Create and return database connection."""
    try:
        print(f"Connecting to PostgreSQL database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def create_qdrant_client(qdrant_url):
    """Create and return Qdrant client."""
    try:
        print(f"Connecting to Qdrant at {qdrant_url}...")
        client = QdrantClient(url=qdrant_url)
        return client
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")
        sys.exit(1)


COLLECTION_NAME = "skincareGPT"

def create_collection_if_not_exists(collection_name, size=1536):
    """Create Qdrant collection if it doesn't exist."""
    try:
        qdrant_client = create_qdrant_client("http://localhost:6333")
        # Check if collection exists
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name not in collection_names:
            print(f"Creating collection '{collection_name}'...")
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=size, distance=Distance.COSINE)
            )
            print(f"Collection '{collection_name}' created successfully")
        else:
            print(f"Collection '{collection_name}' already exists")
            
    except Exception as e:
        print(f"Error creating collection: {e}")
        raise
    
    finally:
        if qdrant_client:
            qdrant_client.close()
            print("Qdrant client connection closed")

def clear_collection(collection_name):
    """Clear all data from a Qdrant collection."""
    try:
        qdrant_client = create_qdrant_client("http://localhost:6333")
        
        # Check if collection exists
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if collection_name in collection_names:
            print(f"Clearing all data from collection '{collection_name}'...")
            
            # Delete the collection entirely and recreate it
            qdrant_client.delete_collection(collection_name)
            print(f"Collection '{collection_name}' deleted")
            
            # Recreate the collection
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
            print(f"Collection '{collection_name}' recreated and ready for new data")
        else:
            print(f"Collection '{collection_name}' does not exist")
            
    except Exception as e:
        print(f"Error clearing collection: {e}")
        raise
    
    finally:
        if qdrant_client:
            qdrant_client.close()
            print("Qdrant client connection closed")

def migrate_products_to_qdrant(limit: int = None):
    load_dotenv()

    # Database and Qdrant configuration
    db_url = os.getenv("DATABASE_URL")
    qdrant_url = "http://localhost:6333"

    # Create database connection
    db_conn = create_database_connection(db_url)

    # Create Qdrant client
    qdrant_client = create_qdrant_client(qdrant_url)
    
    # Create collection if it doesn't exist
    create_collection_if_not_exists(COLLECTION_NAME)

    try:
        # Fetch products from SQL database
        print("Fetching products from database...")
        cursor = db_conn.cursor()
        
        # Select all products with their details
        if limit:
            query = f"""
                SELECT product_id, product_name, brand_name, price_usd, rating, 
                       reviews, size, ingredients, highlights, primary_category, 
                       secondary_category, teritary_category, loves_count
                FROM sephora_product
                ORDER BY product_id
                LIMIT {limit}
            """
        else:
            query = """
                SELECT product_id, product_name, brand_name, price_usd, rating, 
                    reviews, size, ingredients, highlights, primary_category, 
                    secondary_category, teritary_category, loves_count
                FROM sephora_product
                ORDER BY product_id
            """
        
        cursor.execute(query)
        products = cursor.fetchall()
        
        print(f"Found {len(products)} products to process")
        
        # Process each product
        for i, product in enumerate(products):
            product_id, product_name, brand_name, price_usd, rating, reviews, size, ingredients, highlights, primary_category, secondary_category, teritary_category, loves_count = product
            
            print(f"Processing product {i+1}/{len(products)}: {product_name}")
            
            # Create product data dictionary for embedding
            product_data = {
                'type': 'product',
                'product_id': product_id,
                'product_name': product_name,
                'brand_name': brand_name,
                'price_usd': price_usd,
                'rating': rating,
                'reviews': reviews,
                'size': size,
                'ingredients': ingredients,
                'highlights': highlights,
                'primary_category': primary_category,
                'secondary_category': secondary_category,
                'tertiary_category': teritary_category,
                'loves_count': loves_count
            }
            
            # Create embedding for the product
            try:
                embedding = create_product_embedding(
                    product_name=product_name,
                    brand_name=brand_name,
                    primary_category=primary_category,
                    secondary_category=secondary_category,
                    tertiary_category=teritary_category,
                    price_usd=price_usd,
                    highlights=highlights if highlights else [],
                    ingredients=ingredients if ingredients else [],
                    model="text-embedding-3-small"
                )
                
                # Insert into Qdrant
                point = {
                    "id": str(uuid.uuid4()),  # Generate a unique ID for the point
                    "vector": embedding,
                    "payload": product_data
                }
                
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[point]
                )
                
                if (i + 1) % 100 == 0:
                    print(f"Processed {i + 1} products...")
                    
            except Exception as e:
                print(f"Error processing product {product_id}: {e}")
                continue
        
        print(f"Successfully processed {len(products)} products")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        db_conn.rollback()
        
    finally:
        # Clean up connections
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()
        print("Database connection closed")

def migrate_reviews_to_qdrant(limit: int = None):
    load_dotenv()

    # Database and Qdrant configuration
    db_url = os.getenv("DATABASE_URL")
    qdrant_url = "http://localhost:6333"

    # Create database connection
    db_conn = create_database_connection(db_url)

    # Create Qdrant client
    qdrant_client = create_qdrant_client(qdrant_url)
    
    # Create collection if it doesn't exist
    create_collection_if_not_exists(COLLECTION_NAME)

    try:
        # Fetch reviews from SQL database
        print("Fetching reviews from database...")
        cursor = db_conn.cursor()
        
        # Select all reviews with their details
        if limit:
            query = f"""
                SELECT review_id, product_id, author_id, is_recommended, rating, review_title, review_text, 
                       helpfulness, total_feedback_count, total_neg_feedback_count, total_pos_feedback_count, 
                       submission_time, skin_tone, eye_color, skin_type, hair_color, 
                       product_name, brand_name, price_usd
                FROM sephora_review
                ORDER BY review_id
                LIMIT {limit}
            """
        else:
            query = """
                SELECT review_id, product_id, author_id, is_recommended, rating, review_title, review_text, 
                       helpfulness, total_feedback_count, total_neg_feedback_count, total_pos_feedback_count, 
                       submission_time, skin_tone, eye_color, skin_type, hair_color, 
                       product_name, brand_name, price_usd
                FROM sephora_review
                ORDER BY review_id
            """
        
        cursor.execute(query)
        reviews = cursor.fetchall()
        
        print(f"Found {len(reviews)} reviews to process")
        
        # Process each review
        for i, review in enumerate(reviews):
            (review_id, product_id, author_id, is_recommended, rating, review_title, review_text, helpfulness, 
             total_feedback_count, total_neg_feedback_count, total_pos_feedback_count, submission_time, 
             skin_tone, eye_color, skin_type, hair_color, product_name, brand_name, price_usd) = review
            
            print(f"Processing review {i+1}/{len(reviews)}: {review_id}")
            
            # Create review data dictionary for embedding
            review_data = {
                'type': 'review',
                'review_id': review_id,
                'product_id': product_id,
                'author_id': author_id,
                'is_recommended': is_recommended,
                'rating': rating,
                'review_title': review_title,
                'review_text': review_text,
                'helpfulness': helpfulness,
                'total_feedback_count': total_feedback_count,
                'total_neg_feedback_count': total_neg_feedback_count,
                'total_pos_feedback_count': total_pos_feedback_count,
                'submission_time': submission_time,
                'skin_tone': skin_tone,
                'eye_color': eye_color,
                'skin_type': skin_type,
                'hair_color': hair_color,
                'product_name': product_name,
                'brand_name': brand_name,
                'price_usd': price_usd
            }
            
            # Create embedding for the review
            try:
                embedding = create_review_embedding(
                    review_text=review_text,
                    review_title=review_title,
                    product_name=product_name,
                    skin_tone=skin_tone,
                    eye_color=eye_color,
                    skin_type=skin_type,
                    hair_color=hair_color,
                    is_recommended=is_recommended,
                    rating=rating,
                    model="text-embedding-3-small"
                )
                
                # Insert into Qdrant
                point = {
                    "id": str(uuid.uuid4()),  # Generate a unique ID for the point
                    "vector": embedding,
                    "payload": review_data
                }
                
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[point]
                )
                
                if (i + 1) % 100 == 0:
                    print(f"Processed {i + 1} reviews...")
                    
            except Exception as e:
                print(f"Error processing review {review_id}: {e}")
                continue
        
        print(f"Successfully processed {len(reviews)} reviews")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        db_conn.rollback()
        
    finally:
        # Clean up connections
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()
        print("Database connection closed")

def main():
    # Load environment variables
    clear_collection(COLLECTION_NAME)
    migrate_products_to_qdrant(size=200)
    migrate_reviews_to_qdrant(size=200)


if __name__ == "__main__":
    main()
    create_collection_if_not_exists('SkincareGPT_768', size=768)  # Create a separate collection for 768 embeddings