from httpx import AsyncClient, Response
from app.config.config import settings
from app.log.log import serialization_results_json


async def route(
    path: str,
    method: str,
    data: dict = {},
    json: dict = {},
    params: dict = {},
    headers: dict = {}
) -> 'Response':

    async with AsyncClient(
        base_url=settings.core_url, headers=headers
    ) as client:
        request = client.build_request(
            url=path, method=method, data=data, json=json, params=params
        )
        response = await client.send(request)
        return response

# TODO: на этом уровне у функций создать обработчик исключений
# TODO: если тело ответа будет содержать "error" -> вызвать исключение -> записать в лог
# TODO: затем вернуть ответ пользователю о неисправности
# TODO: главное что бы бот после исключения не падал, а продолжал работать


# TODO: регистрация авторизация и создание диалога реализовать в рамках одной сессии к ядру


@serialization_results_json
async def create_user_in_core(
    email: str, password: str, user_tg_id: int
):
    response = (
        await route(
            "users/", "POST",
            json={"email": email, "password": str(password)}
        )
    )
    return response, user_tg_id


@serialization_results_json
async def login_user_in_core(
    email: str, password: str, user_tg_id: int
):
    response = (
        await route(
            "users/login/", "POST",
            json={"email": email, "password": str(password)}
        )
    )
    return response, user_tg_id


@serialization_results_json
async def create_dialog(
    token: str, name: str, model_id: int, user_tg_id: int
):
    response = (
        await route(
            "dialogues/", "POST",
            json={"name": name, "bot_id": model_id},
            headers={"Authorization": f"Bearer {token}"}
        )
    )
    return response, user_tg_id


@serialization_results_json
async def create_message(
    user_tg_id: int,
    token: str,
    dialog_id: int,
    model_id: int,
    text: str
):
    response = await route(
        f"dialogues/{dialog_id}/messages", "POST",
        json={"bot_id": model_id, "text": text},
        headers={'Authorization': f'Bearer {token}'}
    )
    return response, user_tg_id


@serialization_results_json
async def list_models(user_tg_id: int):
    response = await route(
        "bots/", "GET"
    )
    return response, user_tg_id


"""
@serialization_results_json
async def optionally_update_dialog(
    token: str,
    dialogue_id: int,
    dialogue_name: str,
):
    response = (
        await route(
            f"dialogues/{dialogue_id}/", "PATCH",
            json={"name": dialogue_name},
            headers={"Authorization": f"Bearer {token}"}
        )
    )
    return response
"""