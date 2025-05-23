import os
import redis
import json
import pickle
from typing import Any, Dict, List, Optional, Union

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

class RedisClient():
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        value = json.dumps(value)
        return self.client.set(key, value, ex=ex)

    def get(self, key: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
        value = self.client.get(key)
        if value is None:
            return None
        return json.loads(value)
        
    def delete(self, key: str) -> int:
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        return self.client.exists(key) == 1
    
    def expire(self, key: str, timeout: int) -> bool:
        return self.client.expire(key, timeout)
    
    def setex(self, key: str, value: Any, timeout: int) -> bool:
        value = json.dumps(value)
        return self.client.setex(key, timeout, value)