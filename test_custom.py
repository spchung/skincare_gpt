from app.memory.postgres_memory import EntityTrackingSession
from app.models.sephora import SephoraProductSQLModel, SephoraProductViewModel
from app.internal.postgres import get_db

if __name__ == '__main__':
    thread_id = '123'
    db = EntityTrackingSession(next(get_db()), thread_id)
    product_ids = ["P122718"]

    q = db.query(SephoraProductSQLModel)

    name = "Glow Oil Body Sunscreen SPF 50 PA++++"
    brand_name = "Supergoop!!!!"
    if name is not None:
        q = q.filter(SephoraProductSQLModel.product_name.like(f"%{name}%"))
    if brand_name is not None:
        q = q.filter(SephoraProductSQLModel.brand_name.like(f"%{brand_name}%"))

    res = q.first()
    if res is not None:
        print(res.__dict__)