from sqlalchemy.orm import Session
from typing import List, Any, Type
import logging
from app.internal.redis import RedisClient
from app.models.sephora import SephoraReviewRedisModel, SephoraProductRedisModel

class EntityTrackingSession:
    def __init__(self, session: Session, thread_id: str, entities_limit: int = 8):
        self.redis_client = RedisClient()
        self.redis_key = f"entities:{thread_id}"
        self.entities_limit = entities_limit
        self._session = session
        self.retrieved_items = []
        self.logger = logging.getLogger(__name__)
    
    def query(self, model_class: Type):
        return TrackedQuery(self._session.query(model_class), self, model_class)
    
    def log_retrieval(self, model_class: Type, items: List[Any]):
        count = len(items) if hasattr(items, '__len__') else 1
        self.logger.info(f"Retrieved {count} {model_class.__name__} objects")
        
        ## items
        self.retrieved_items.extend(items if isinstance(items, list) else [items])
        self.set_itmes_in_redis()

    def set_itmes_in_redis(self):
        """
        set on key 'entities' in the root redis object
        """
        if not self.retrieved_items:
            return
        # Convert items to a list of dictionaries
        redis_ents = []
        for item in self.retrieved_items:
            # print(item.__dict__['product_id'])
            if item.__class__.__name__ == 'SephoraProductSQLModel':
                redis_ents.append(SephoraProductRedisModel(**item.__dict__))
            elif item.__class__.__name__ == 'SephoraReviewSQLModel':
                redis_ents.append(SephoraReviewRedisModel(**item.__dict__))
        
        json_payload = [redis_item.model_dump() for redis_item in redis_ents]

        # get if exist
        if not self.redis_client.exists(self.redis_key):
            self.redis_client.setex(self.redis_key, json_payload, 86400)
        else:
            # get the existing list
            record = self.redis_client.get(self.redis_key)
            if record:
                record.extend(json_payload)
                if len(record) > self.entities_limit:
                    record = record[-self.entities_limit:]
                self.redis_client.setex(self.redis_key, record, 86400)

    def __getattr__(self, name):
        # Delegate other session methods to the underlying session
        return getattr(self._session, name)

    ## context manager protocol
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()    
        except Exception as e:
            self.logger.error(f"Error during session handling: {e}")
        finally:
            self._session.close()
            # Clear retrieved items after session ends
            self.retrieved_items.clear()
            # Optionally, clear the Redis key
            # self.redis_client.delete(self.redis_key)
        
class TrackedQuery:
    def __init__(self, query, tracked_session: EntityTrackingSession, model_class: Type):
        self._query = query
        self._tracked_session = tracked_session
        self._model_class = model_class
    
    def filter(self, *args, **kwargs):
        self._query = self._query.filter(*args, **kwargs)
        return self
    
    def all(self):
        results = self._query.all()
        self._tracked_session.log_retrieval(self._model_class, results)
        return results
    
    def first(self):
        result = self._query.first()
        if result:
            self._tracked_session.log_retrieval(self._model_class, [result])
        return result
    
    def one(self):
        result = self._query.one()
        self._tracked_session.log_retrieval(self._model_class, [result])
        return result
    
    def __getattr__(self, name):
        # Delegate other query methods to the underlying query
        attr = getattr(self._query, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                # If it returns a query, wrap it
                if hasattr(result, 'all'):
                    return TrackedQuery(result, self._tracked_session, self._model_class)
                return result
            return wrapper
        return attr