from app.config.redis import client_redis
from app.config.config import settings

__user_dialogue = settings.USER_DIALOGUE_INFO
__telegram_email = settings.TELEGRAM_EMAIL


async def set_token_in_cache(
    email: str, token: str, expires_in: int
):
    expires_in -= 100  # уменьшил время жизни токена на 100 с
    async with client_redis() as client:
        await client.set(
            name=email,
            value=token,
            exat=expires_in
        )


async def get_token_from_cache(email: str):
    async with client_redis() as client:
        result = await client.get(name=email)
    return result


async def del_token_from_cache(user_tg_id: int):
    email = __telegram_email % user_tg_id
    async with client_redis() as client:
        await client.delete(email)


async def set_user_dialogue_in_cache(
    user_tg_id: int, model_id: int, dialogue_id: int
):
    name = __user_dialogue % user_tg_id
    async with client_redis() as client:
        await client.hset(
            name=name,
            mapping={"model_id": model_id, "dialogue_id": dialogue_id}
        )


async def get_user_dialogue_from_cache(user_tg_id: int):
    name = __user_dialogue % user_tg_id
    async with client_redis() as client:
        result = await client.hgetall(name=name)
    return result


async def del_user_dialogue_from_cache(user_tg_id: int):
    name = __user_dialogue % user_tg_id
    async with client_redis() as client:
        result = await client.delete(name)
    return result


