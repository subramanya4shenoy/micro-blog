import os 
import json
import redis
from typings import Any, Optional
from logging_config import get_logger

logger = get_logger("cache")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_json(key: str) -> Optional[Any]:
    """ Get JSON data from Redis """
    try:
        raw = redis_client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Error getting JSON data from Redis: {e}")
        return None

def set_josn(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """ Set JSON data in Redis """
    try:
        data = json.dumps(value, default=str)
        if ttl is not None:
            redis_client.setex(key, ttl, data)
        else:
            redis_client.set(key, data)
    except Exception as e:
        logger.error(f"Error setting JSON data in Redis: {e}")

def delete_key(key: str) -> None:
    """ Delete key from Redis """
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.error(f"Error deleting key from Redis: {e}")


def delete_pattern(pattern: str) -> None:
    """ Delete keys by pattern from Redis """
    try:
        for k in redis_client.key(pattern):
            redis_client.delete(k)
    except Exception as e:
        logger.error(f"Error deleting keys by pattern from Redis: {e}")