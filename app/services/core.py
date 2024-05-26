from decimal import Decimal
import yaml
from tiktoken import get_encoding
from app.config.config import settings
from app.log.log import (
    ApplicationUserError,
    InternalServerError,
    RateLimitError,
    msg_limit_error,
    msg_error_answer,
    logger_raw_exc
)
from app.bot.text import (
    msg_choices_model,
    msg_context,
    msg_auth_success,
    msg_balance,
    msg_list_models,
    msg_negative_balance
)
from app.crud.users import (
    get_user_dialogue_from_db,
    inc_number_dialogue_user,
    update_dialogue_user,
    update_user_model_in_db,
    get_user_balance_from_db,
    decrement_user_balance_in_db
)
from app.core_api.route import (
    create_dialog,
    create_message,
    list_models,
    route_cbr
)
from .auth import authentication_user
from .cache import (
    get_user_dialogue_from_cache,
    set_user_dialogue_in_cache,
    del_user_dialogue_from_cache,
    set_price_parameters_in_cache,
    get_price_parameters_from_cache
)


__dialogue_name = settings.NAME_DIALOGUE_MODEL


async def authentication_user_in_system(user_tg_id: int):
    message_answer = "%s"
    try:
        await authentication_user(user_tg_id)

    except Exception as exc:
        message_answer = message_answer % msg_error_answer
        logger_raw_exc.error(exc_info=True, msg=exc.args)

    else:
        message_answer = message_answer % msg_auth_success

    return message_answer


async def create_messages(user_tg_id: int, messages_user: str):

    token = await authentication_user(user_tg_id)

    user_balance = await get_user_balance_from_db(user_tg_id)
    if not user_balance:
        return msg_negative_balance

    user_dialogue = await get_user_dialogue_from_cache(user_tg_id)
    message_answer = "%s"
    if user_dialogue:
        model_id, dialogue_id = user_dialogue["model_id"], user_dialogue["dialogue_id"]

    else:
        model_id, dialogue_id, number_dialogue = await get_user_dialogue_from_db(user_tg_id)

        if not number_dialogue and not dialogue_id:
            dialogue_id = await new_dialogue_user(
                token=token,
                model_id=model_id,
                user_tg_id=user_tg_id,
                number_dialogue=number_dialogue
            )

        await set_user_dialogue_in_cache(
            user_tg_id=user_tg_id,
            model_id=model_id,
            dialogue_id=dialogue_id
        )

    try:
        response = await create_message(
            user_tg_id=user_tg_id,
            token=token,
            model_id=model_id,
            dialog_id=dialogue_id,
            text=messages_user
        )
    except ApplicationUserError:

        token = await authentication_user(user_tg_id=user_tg_id)

        response = await create_message(
            user_tg_id=user_tg_id,
            token=token,
            model_id=model_id,
            dialog_id=dialogue_id,
            text=messages_user
        )
        message_answer = message_answer % response[-1]["text"]

        await calculate_amount_tokens(
            messages=response, user_tg_id=user_tg_id
        )

    except RateLimitError as exc:
        message_answer = message_answer % (msg_limit_error % exc.delay)

    except Exception as exc:
        message_answer = message_answer % msg_error_answer
        logger_raw_exc.error(exc_info=True, msg=exc.args)

    else:
        message_answer = message_answer % response[-1]["text"]

        await calculate_amount_tokens(
            messages=response, user_tg_id=user_tg_id
        )

    return message_answer


async def new_context(user_tg_id: int):
    user_balance = await get_user_balance_from_db(user_tg_id)
    if not user_balance:
        return msg_negative_balance

    message_answer = "%s"
    try:
        token = await authentication_user(user_tg_id)
        model_id, number_dialogue = await inc_number_dialogue_user(user_tg_id)

        dialogue_id = await new_dialogue_user(
            token=token,
            model_id=model_id,
            user_tg_id=user_tg_id,
            number_dialogue=number_dialogue
        )
        await set_user_dialogue_in_cache(
            user_tg_id=user_tg_id,
            model_id=model_id,
            dialogue_id=dialogue_id
        )
    except Exception as exc:
        logger_raw_exc.error(exc_info=True, msg=exc.args)
        message_answer = message_answer % msg_error_answer

    else:
        message_answer = message_answer % msg_context

    return message_answer


async def new_dialogue_user(
    token: str,
    model_id: int,
    user_tg_id: int,
    number_dialogue: int
):
    dialogue_name = __dialogue_name % number_dialogue
    try:
        dialogue_user = await create_dialog(
            user_tg_id=user_tg_id,
            token=token,
            model_id=model_id,
            name=dialogue_name
        )
    except InternalServerError:

        token = await authentication_user(user_tg_id=user_tg_id)

        dialogue_user = await create_dialog(
            user_tg_id=user_tg_id,
            token=token,
            model_id=model_id,
            name=dialogue_name
        )

        dialogue_id = dialogue_user["id"]

        await update_dialogue_user(
            user_tg_id=user_tg_id,
            dialogue_id=dialogue_id,
        )
        return dialogue_id

    else:
        dialogue_id = dialogue_user["id"]

        await update_dialogue_user(
            user_tg_id=user_tg_id,
            dialogue_id=dialogue_id,
        )
        return dialogue_id


async def get_list_models(user_tg_id: int):
    message_answer = "%s"
    active_models = {}
    try:
        models = await list_models(user_tg_id=user_tg_id)
    except Exception as exc:
        models, message_answer = active_models, message_answer % msg_error_answer
        logger_raw_exc.error(exc_info=True, msg=exc.args)

    else:
        for model in models:
            if model["available"] and model["status_code"] == "active":
                active_models[model["name"]] = model["id"]

        models, message_answer = active_models, message_answer % msg_list_models

    return models, message_answer


async def set_model_user(
    user_tg_id: int,
    model_id: int,
    model_name: str,
):
    message_answer = "%s"
    try:
        await update_user_model_in_db(
            user_tg_id=user_tg_id,
            model_id=model_id,
            model_name=model_name
        )
    except Exception as exc:
        logger_raw_exc.error(exc_info=True, msg=exc.args)
        message_answer = message_answer % msg_error_answer

    else:
        message_answer = message_answer % msg_choices_model
        await del_user_dialogue_from_cache(user_tg_id)

    return message_answer


async def get_user_balance(user_tg_id: int):
    message_answer = "%s"
    try:
        balance = await get_user_balance_from_db(user_tg_id=user_tg_id)

    except Exception as exc:
        logger_raw_exc.error(exc_info=True, msg=exc.args)
        message_answer = message_answer % msg_error_answer

    else:
        message_answer = message_answer % (msg_balance % round(balance, 6))

    return message_answer


async def calculate_amount_tokens(
    messages: list, user_tg_id: int
):
    currency, input_price, output_price = await get_current_value_currency()

    encoding = get_encoding("cl100k_base")

    num_tokens_user = len(encoding.encode("".join(
        (messages[-2]["author"]["role"], messages[-2]["author"]["name"], messages[-2]["text"])
    )))
    num_tokens_models = len(encoding.encode("".join(
        (messages[-1]["author"]["role"], messages[-1]["author"]["name"], messages[-1]["text"])
    )))

    price_message = Decimal(
        (
            (num_tokens_user * input_price + num_tokens_models * output_price)
            / 1000000
        )
        * currency
        * Decimal(1.5)
    )
    await decrement_user_balance_in_db(user_tg_id=user_tg_id, amount=price_message)


async def get_current_value_currency():
    price_param = await get_price_parameters_from_cache()
    if price_param:
        return Decimal(price_param["USD"]), Decimal(price_param["input_price"]), Decimal(price_param["output_price"])
    #
    # currency = await get_current_currency_from_cbr_api()
    #
    # with open("app/price.yaml") as f:
    #     data = yaml.safe_load(f)
    #
    # input_price, output_price = data["input_price"], data["output_price"]
    #
    # await set_price_parameters_in_cache(
    #     currency=currency,
    #     input_price=input_price,
    #     output_price=output_price
    # )
    #
    # return currency, input_price, output_price

