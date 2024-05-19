from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.log.log import (
    msg_error_answer,
    msg_limit_error,
    RateLimitError,
)
from app.log.config import logger
from app.bot.keyboards import model_buttons
from app.bot.states import ChoicesModels

from app.services.core import (
    create_messages,
    new_context,
    get_list_models,
    authentication_user,
    set_model_user
)


router = Router()


@router.message(Command("start"))
async def start(msg: Message):
    try:
        await authentication_user(msg.from_user.id)
    except Exception as exc:
        logger.error(exc_info=True, msg=exc.args)
        await msg.answer(msg_error_answer)
    else:
        await msg.answer(f"I am bot GPT")


@router.message(Command("context"))
async def reset_context(msg: Message):
    try:
        await new_context(msg.from_user.id)
    except Exception as exc:
        logger.error(exc_info=True, msg=exc.args)
        await msg.answer(msg_error_answer)
    else:
        await msg.answer(f"Контекст сброшен")


@router.message(Command("balance"))
async def get_balance(msg: Message):
    await msg.answer("Ваш баланс: 0")


@router.message(Command("help"))
async def get_help(msg: Message):
    await msg.answer("help")


@router.message(Command("models"))
async def model_choices_state(msg: Message, state: FSMContext):
    await state.set_state(ChoicesModels.model_choices)
    try:
        models = await get_list_models(msg.from_user.id)
    except Exception as exc:
        logger.error(exc_info=True, msg=exc.args)
        await msg.answer(msg_error_answer)
    else:
        await state.update_data(models)

        await msg.answer(
            "выберите модель",
            reply_markup=model_buttons(models.keys())
        )


@router.message(StateFilter(ChoicesModels.model_choices), F.text)
async def user_choices_model(msg: Message, state: FSMContext):
    data = await state.get_data()
    if msg.text.lower() in data:

        await set_model_user(
            user_tg_id=msg.from_user.id,
            model_id=int(data[msg.text]),
            model_name=msg.text
        )
        await msg.answer("Модель изменена")
        await state.clear()
    else:
        await state.clear()
        await messages_bot(msg)


@router.message(F.text)
async def messages_bot(msg: Message):
    try:
        response_bot = await create_messages(msg.from_user.id, msg.text)

    except RateLimitError as exc:
        await msg.answer(msg_limit_error % exc.delay)

    except Exception as exc:
        logger.error(exc_info=True, msg=exc.args)
        await msg.answer(msg_error_answer)

    else:
        await msg.answer(response_bot)


