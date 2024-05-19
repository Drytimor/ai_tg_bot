import redis.asyncio as redis
from redis.asyncio.client import Redis
from contextlib import asynccontextmanager


@asynccontextmanager
async def client_redis() -> "Redis":
    client = redis.Redis(decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()







