import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app.db.milvus import client
from pymilvus import DataType

collection_name = "product_title"

try:
    res = client.get_collection_stats(collection_name)
    client.drop_collection(collection_name)
    q = input(f"Are you sure you want to drop the collection ({collection_name})? (y/n): ")
    if q == "y":
        client.drop_collection(collection_name)
    else:
        print("Did nothing.")
        sys.exit()
    
except Exception as e:
    print("collection not found - continue")

productSchema = client.create_schema()

# corresponds to pgProduct.id
productSchema.add_field(field_name='id', datatype=DataType.INT64, is_primary=True, auto_id=False)
# primary key - unique
productSchema.add_field(field_name='parent_asin', datatype=DataType.VARCHAR, max_length=256)
productSchema.add_field(field_name='title', datatype=DataType.VARCHAR, max_length=1024)
# text-embedding-3-small
productSchema.add_field(field_name='title_vector', datatype=DataType.FLOAT16_VECTOR, dim=1536)

# Prepare index parameters
index_params = client.prepare_index_params()

index_params.add_index(
    field_name="id",
    index_type="STL_SORT"
)

index_params.add_index(
    field_name="title_vector", 
    index_type="AUTOINDEX",
    metric_type="COSINE"
)

client.create_collection(
    collection_name="product_title",
    schema=productSchema,
    index_params=index_params
)

res = client.get_load_state(
    collection_name="product_title"
)