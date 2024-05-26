import logging
from fastapi import APIRouter, Request
from fastapi.responses import Response
from aiogram.types import Update
from yookassa.domain.common import SecurityHelper
from app.bot.main import bot, dp
from app.bot.text import (
    msg_success_up_balance,
    msg_fail_up_balance,
)
from app.services.payment import (
    update_user_payment_status,
    logger_raw_exc,
    msg_payment_error,
    PaymentError
)


router = APIRouter(
    prefix="/webhook",
    tags=['webhook']
)


@router.post('/bot')
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


@router.post("/yookassa")
async def webhook_payment_status_from_yookassa(request: Request):

    ip = request.client.host
    if not SecurityHelper().is_ip_trusted(ip):
        return Response(status_code=400)

    webhook_data = await request.json()
    try:
        user_chat_id, massage_answer = await update_user_payment_status(webhook_data=webhook_data)

    except PaymentError as exc:
        await bot.send_message(
            chat_id=webhook_data["object"]["metadata"]["user_chat_id"], text=exc.msg
        )
        return Response(status_code=400)

    else:
        await bot.send_message(user_chat_id, massage_answer)
        return Response(status_code=200)

