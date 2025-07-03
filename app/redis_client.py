import redis
from app.settings import settings

# Create Redis connection
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis():
    return redis_client
