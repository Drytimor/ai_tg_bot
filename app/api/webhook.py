from fastapi import APIRouter
from aiogram.types import Update
from app.bot.main import bot, dp


router = APIRouter(
    prefix="/webhook",
    tags=['webhook']
)


@router.post('/bot')
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)

