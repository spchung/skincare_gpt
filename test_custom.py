from app.memory.postgres_memory import TrackedSession
from app.models.sephora import SephoraProductSQLModel, SephoraProductViewModel
from app.internal.postgres import get_db

if __name__ == '__main__':
    thread_id = '123'
    db = TrackedSession(next(get_db()), thread_id)
    product_ids = ["P122718"]
    
    sql_products = db.query(SephoraProductSQLModel).filter(SephoraProductSQLModel.product_id.in_(product_ids)).all()
    # prod = SephoraProductViewModel(**db.retrieved_items[0].__dict__)

    # print(prod.ingredients)