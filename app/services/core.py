from app.log.log import ApplicationUserError, InternalServerError
from .auth import authentication_user
from .cache import (
    get_user_dialogue_from_cache,
    set_user_dialogue_in_cache,
    del_user_dialogue_from_cache,
)
from app.config.config import settings
from app.crud.users import (
    get_user_dialogue_from_db,
    inc_number_dialogue_user,
    update_dialogue_user,
    update_user_model_in_db
)
from app.core_api.route import (
    create_dialog, create_message,
    list_models
)


__dialogue_name = settings.NAME_DIALOGUE_MODEL


async def create_messages(user_tg_id: int, messages_user: str):
    token = await authentication_user(user_tg_id)
    user_dialogue = await get_user_dialogue_from_cache(user_tg_id)
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

        # await asyncio.sleep(0.5)

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

        return response[-1]["text"]
    else:
        return response[-1]["text"]


async def new_context(user_tg_id: int):
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
    models = await list_models(user_tg_id=user_tg_id)
    active_models = {}
    for model in models:
        if model["available"] and model["status_code"] == "active":
            active_models[model["name"]] = model["id"]

    return active_models


async def set_model_user(
    user_tg_id: int,
    model_id: int,
    model_name: str,
):
    await update_user_model_in_db(
        user_tg_id=user_tg_id,
        model_id=model_id,
        model_name=model_name
    )
    await del_user_dialogue_from_cache(user_tg_id)

