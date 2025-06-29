#!/usr/bin/env python3
"""
Data migration script for Sephora product and review data.
This script executes SQL files to create tables and import data.
"""

import psycopg2
import os
import sys
from pathlib import Path
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

def execute_sql_file(conn, sql_file_path):
    """Execute SQL commands from a file."""
    cursor = conn.cursor()
    
    try:
        print(f"📄 Executing SQL file: {sql_file_path.name}")
        
        # Read SQL file
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split into individual statements (basic approach)
        # More sophisticated parsing might be needed for complex SQL
        statements = []
        current_statement = ""
        
        for line in sql_content.split('\n'):
            # Skip comment lines
            if line.strip().startswith('--') or not line.strip():
                continue
                
            current_statement += line + '\n'
            
            # If line ends with semicolon, it's end of statement
            if line.strip().endswith(';'):
                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ""
        
        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # Execute statements
        statement_count = 0
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                    statement_count += 1
                    
                    # Show progress for INSERT statements
                    if statement.strip().upper().startswith('INSERT'):
                        if statement_count % 100 == 0:
                            print(f"📈 Processed {statement_count} statements...")
                            
                except psycopg2.Error as e:
                    print(f"❌ Error executing statement: {e}")
                    print(f"Statement: {statement[:100]}...")
                    conn.rollback()
                    raise
        
        conn.commit()
        print(f"✅ Successfully executed {statement_count} SQL statements from {sql_file_path.name}")
        
    except Exception as e:
        print(f"❌ Error executing SQL file {sql_file_path.name}: {e}")
        conn.rollback()
        sys.exit(1)

def create_indexes(conn):
    """Create indexes for better query performance."""
    cursor = conn.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_products_brand ON sephora_product(brand_name);",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON sephora_product(primary_category);",
        "CREATE INDEX IF NOT EXISTS idx_products_rating ON sephora_product(rating);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON sephora_review(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_rating ON sephora_review(rating);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_submission_time ON sephora_review(submission_time);",
        "CREATE INDEX IF NOT EXISTS idx_reviews_skin_type ON sephora_review(skin_type);"
    ]
    
    try:
        print("📊 Creating database indexes...")
        for index_sql in indexes:
            cursor.execute(index_sql)
        conn.commit()
        print("✅ Database indexes created successfully")
    except psycopg2.Error as e:
        print(f"❌ Error creating indexes: {e}")

def validate_data(conn):
    """Validate imported data."""
    cursor = conn.cursor()
    
    try:
        # Check product count
        cursor.execute("SELECT COUNT(*) FROM sephora_product;")
        product_count = cursor.fetchone()[0]
        
        # Check review count
        cursor.execute("SELECT COUNT(*) FROM sephora_review;")
        review_count = cursor.fetchone()[0]
        
        # Check for orphaned reviews
        cursor.execute("""
            SELECT COUNT(*) FROM sephora_review r 
            LEFT JOIN sephora_product p ON r.product_id = p.product_id 
            WHERE p.product_id IS NULL AND r.product_id != '';
        """)
        orphaned_reviews = cursor.fetchone()[0]
        
        print(f"\n📋 Data Validation Results:")
        print(f"   Products imported: {product_count}")
        print(f"   Reviews imported: {review_count}")
        print(f"   Orphaned reviews: {orphaned_reviews}")
        
        if orphaned_reviews > 0:
            print(f"⚠️  Warning: {orphaned_reviews} reviews reference non-existent products")
        else:
            print("✅ All reviews properly linked to products")
            
    except psycopg2.Error as e:
        print(f"❌ Error during validation: {e}")

def main():
    """Main execution function."""
    load_dotenv()
    print("🚀 Starting Sephora data migration...")
    
    # Set up paths
    script_dir = Path(__file__).parent
    products_sql = script_dir / "sephora_product.sql"
    reviews_sql = script_dir / "sephora_review.sql"
    db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        print(f"❌ DATABASE_URL environment variable is not provided")
        sys.exit(1)
    
    # Check if SQL files exist
    if not products_sql.exists():
        print(f"❌ Products SQL file not found: {products_sql}")
        sys.exit(1)
    
    if not reviews_sql.exists():
        print(f"❌ Reviews SQL file not found: {reviews_sql}")
        sys.exit(1)
    
    # Create database connection
    conn = create_database_connection(db_url)
    
    try:
        # Execute SQL files
        execute_sql_file(conn, products_sql)
        execute_sql_file(conn, reviews_sql)
        
        # Create indexes
        create_indexes(conn)
        
        # Validate data
        validate_data(conn)
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"💾 Data imported to PostgreSQL database")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()