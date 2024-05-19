from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import webhook
from app.config.config import settings
from app.bot.main import bot
from app.bot.keyboards import main_menu_commands
from app.log.config import queue_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url=settings.bot_webhook_url)
    await bot.set_my_commands(main_menu_commands)
    queue_handler.listener.start()
    yield
    await bot.delete_webhook()
    queue_handler.listener.stop()

app = FastAPI(lifespan=lifespan)


app.include_router(
    webhook.router
)
# context
# models
# balance
# start
# help


