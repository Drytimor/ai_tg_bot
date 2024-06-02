import asyncio
from aiogram import Router, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
)
from app.bot.keyboards import model_buttons, payment_button
from app.bot.states import (
    ChoicesModels,
    Payments
)
from app.bot.text import (
    msg_help,
    msg_invalid_input_payments,
)
from app.services.cache import check_context_limit, set_context_limit_in_cache
from app.services.core import (
    authentication_user_in_system,
    create_messages,
    new_context,
    display_list_models,
    set_model_user,
    display_user_balance,
)
from app.services.payment import create_payment_for_user

router = Router()


@router.message(Command("start"))
async def start(msg: Message, state: FSMContext):
    await state.clear()
    message_answer = await authentication_user_in_system(msg.from_user.id)
    await msg.answer(message_answer)


@router.message(Command("context"))
async def reset_context(msg: Message, state: FSMContext):
    await state.clear()
    message_answer = await new_context(msg.from_user.id)
    await msg.answer(message_answer)


@router.message(Command("balance"))
async def get_balance(msg: Message, state: FSMContext):
    await state.clear()
    message_answer = await display_user_balance(msg.from_user.id)
    await msg.answer(
        message_answer,
        reply_markup=payment_button()
    )


@router.message(Command("help"))
async def get_help(msg: Message, state: FSMContext):
    await state.clear()
    await set_context_limit_in_cache(msg.from_user.id)
    await msg.answer(msg_help)


@router.message(Command("models"))
async def model_choices_state(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ChoicesModels.model_choices)
    models, massage_answer = await display_list_models(msg.from_user.id)
    if models:
        await state.update_data(models)
        await msg.answer(
            massage_answer,
            reply_markup=model_buttons(models.keys())
        )
    else:
        await msg.answer(massage_answer)


@router.message(StateFilter(ChoicesModels.model_choices), F.text)
async def user_choices_model(msg: Message, state: FSMContext):
    data = await state.get_data()
    if msg.text.lower() in data:

        message = await set_model_user(
            user_tg_id=msg.from_user.id,
            model_id=int(data[msg.text]),
            model_name=msg.text
        )
        await msg.answer(message)
    else:
        await messages_bot(msg)

    await state.clear()


@router.message(StateFilter(None), F.text)
async def messages_bot(msg: Message):
    if not await check_context_limit(msg.from_user.id):
        await asyncio.sleep(0.5)
        await msg.delete()

    else:
        await msg.chat.do(action="typing")
        message_answer = await create_messages(msg.from_user.id, msg.text)
        await msg.answer(message_answer, parse_mode=ParseMode.MARKDOWN_V2)


@router.callback_query(StateFilter(None), F.data == "top_up_balance")
async def user_input_amount(clb: CallbackQuery, state: FSMContext):
    await state.set_state(Payments.payment)
    await clb.message.answer("Введите сумму платежа")


@router.message(StateFilter(Payments.payment), F.text.regexp(r"^[1-9]*\d*$"))
async def create_payment(msg: Message, state: FSMContext):
    message_answer = await create_payment_for_user(
        user_tg_id=msg.from_user.id,
        user_chat_id=msg.chat.id,
        amount=msg.text,
    )
    await msg.answer(message_answer)
    await state.clear()


@router.message(StateFilter(Payments.payment), F.text)
async def invalid_input_user_for_payment(msg: Message):
    await msg.answer(msg_invalid_input_payments)


