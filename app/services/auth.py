from app.config.config import settings
from app.log.log import InternalServerError
from app.crud.users import (
    create_user_in_db,
    get_user_from_db
)
from .cache import (
    set_token_in_cache,
    get_token_from_cache,
    del_token_from_cache
)
from app.core_api.route import (
    create_user_in_core,
    login_user_in_core,
)


__telegram_email = settings.TELEGRAM_EMAIL
__first_dialogue_name = settings.FIRST_NAME_DIALOGUE_MODEL
__default_model_id = settings.DEFAULT_ID_GPT_MODEL
__default_model_name = settings.DEFAULT_NAME_GPT_MODEL


async def authentication_user(user_tg_id: int):
    email, password = __telegram_email % user_tg_id, str(user_tg_id)
    token = await get_token_from_cache(email=email)
    if token:
        return token
    else:
        user = await get_user_from_db(user_tg_id=user_tg_id)
        if user:
            token = await authorization(
                user_tg_id=user_tg_id, email=user.email, password=user.password
            )
        else:
            token = await registration(
                user_tg_id=user_tg_id, email=email, password=password
            )
    return token


async def registration(user_tg_id: int, email: str, password: str) -> str:
    core_user = await create_user_in_core(
        email=email, password=password, user_tg_id=user_tg_id
    )
    user_core_id = core_user["user_id"]
    await create_user_in_db(
        user_tg_id=user_tg_id,
        user_core_id=user_core_id,
        email=email,
        password=password,
        model_id=__default_model_id,
        model_name=__default_model_name,
    )

    token = await authorization(
        user_tg_id=user_tg_id, email=email, password=password
    )

    return token


async def authorization(
        user_tg_id: int, email: str, password: str
) -> str:
    user_auth = await login_user_in_core(
        user_tg_id=user_tg_id, email=email, password=password
    )

    token = user_auth["access_token"]
    expires_in = user_auth["expires_in"]
    await set_token_in_cache(
        email=email,
        token=token,
        expires_in=expires_in
    )
    return token


