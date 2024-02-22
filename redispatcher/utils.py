import redis.asyncio as redis
from pydantic import RedisDsn


def create_client(dsn: str | RedisDsn) -> redis.Redis:
    return redis.Redis.from_pool(redis.ConnectionPool.from_url(str(dsn)))
