from httpx import AsyncClient, Response
from app.config.config import settings
from app.log.log import (
    core_json_api_serialization,
    yookassa_json_api_serialization
)


async def route(
    path: str,
    method: str,
    data: dict = {},
    json: dict = {},
    params: dict = {},
    headers: dict = {},
    timeout: float = settings.TIMEOUT_CORE
) -> 'Response':

    async with AsyncClient(
        base_url=settings.core_url, headers=headers, timeout=timeout
    ) as client:
        request = client.build_request(
            url=path, method=method, data=data, json=json, params=params
        )
        response = await client.send(request)
        return response


@core_json_api_serialization
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


@core_json_api_serialization
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


@core_json_api_serialization
async def create_dialog(
    token: str, name: str, model_id: int, user_tg_id: int
):
    response = (
        await route(
            "dialogues/", "POST",
            json={"name": name, "model_id": model_id},
            headers={"Authorization": f"Bearer {token}"}
        )
    )
    return response, user_tg_id


@core_json_api_serialization
async def create_message(
    user_tg_id: int,
    token: str,
    dialog_id: int,
    model_id: int,
    text: str,
):
    response = await route(
        f"dialogues/{dialog_id}/messages", "POST",
        json={"model_id": model_id, "text": text},
        headers={'Authorization': f'Bearer {token}'},
        timeout=settings.TIMEOUT_ANSWER_CORE
    )
    return response, user_tg_id


@core_json_api_serialization
async def list_models(user_tg_id: int):

    response = await route(
        "models/", "GET"
    )
    return response, user_tg_id


@yookassa_json_api_serialization
async def create_payment_in_yookassa(
    user_tg_id: int,
    user_chat_id: int,
    amount: str,
):
    token, idempotence_key = settings.authorization_basic_token, settings.idempotence_key
    headers = {
        "Content-type": "application/json",
        "Idempotence-Key": idempotence_key,
        "Authorization": "Basic %s" % token
    }
    body = {
            "amount": {
                "value": "%s.00" % amount,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "t.me/pgt_ai_payment_bot"
            },
            "refundable": False,
            "capture": True,
            "description": "Пополнение баланса",
            "metadata": {
                "user_chat_id": "%s" % user_chat_id,
                "user_tg_id": "%s" % user_tg_id
            },
            "test": True
        }

    response = await route_yookassa(
        "/payments",
        "POST",
        headers=headers,
        body=body
    )
    return response, user_tg_id


@yookassa_json_api_serialization
async def get_current_info_user_payment(payment_id: str, user_tg_id: int):

    response = await route_yookassa(
        "/payments/%s" % payment_id, "GET",
        headers={"Authorization": "Basic %s" % settings.authorization_basic_token}
    )
    return response, user_tg_id


async def route_yookassa(
    path: str,
    method: str,
    body: dict = {},
    headers: dict = {}
) -> "Response":

    async with AsyncClient(base_url=settings.YOOKASSA_URL, headers=headers) as client:
        request = client.build_request(method=method, url=path, json=body)
        response = await client.send(request)

    return response


# async def route_yookassa(
#     headers: dict, path: str, body: dict
# ) -> "Response":
#     session = requests.Session()
#     retries = Retry(total=10,
#                     backoff_factor=5 / 1000,
#                     allowed_methods=['POST'],
#                     status_forcelist=[202])
#     session.mount('https://', HTTPAdapter(max_retries=retries))
#     response = session.request(
#         "POST",
#         path,
#         headers=headers,
#         json=body,
#         # verify=self.configuration.verify
#     )
#
#     session.close()
#     return response
