from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from app.config.config import settings
from .handlers import commands


bot = Bot(token=settings.BOT_TOKEN)
storage = RedisStorage.from_url(settings.redis_uri, state_ttl=settings.CACHE_DEFAULT_TTL)
dp = Dispatcher(bot=bot, storage=storage)
dp.include_router(commands.router)

