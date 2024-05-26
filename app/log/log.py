import logging
from functools import wraps
from app.services.cache import del_token_from_cache
from app.log.config import (
    user_id,
    user_request,
    user_response,
    user_payment,
    user_error,
    logger_core,
    logger_payment,
    logger_raw_exc
)


class ErrorResponseException(Exception):
    """От ядра пришла ошибка"""


class EmptyResponseException(Exception):
    """Пришло пустое тело от ядра"""


class InternalServerError(Exception):
    """Упало ядро"""
    # def __init__(self, msg):
    #     self.msg = msg


class ApplicationUserError(Exception):
    """Пользователь отвязался от приложения"""


class RateLimitError(Exception):
    """Превышен лимит запросов"""
    def __init__(self, delay: int):
        self.delay = delay
        # self.msg = msg


class PaymentError(Exception):
    """Пришла ошибка от yookassa"""
    def __init__(self, msg=None):
        self.msg = msg


msg_error_answer = """
Возникла непредвиденная ошибка.
Обратитесь в техническую поддержку или попробуйте
перезапустить бота командой /start
"""
msg_limit_error = """
Невозможно обработать запрос из-за высокой нагрузки. Пожалуйста, попробуйте повторить запрос через %d сек
"""
msg_server_error = "error %s"
msg_payment_error = "невозможно провести оплату"


def core_json_api_serialization(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response, user_tg_id = await func(*args, **kwargs)
        if response.status_code == 204:
            user_id.set(user_tg_id)
            user_request.set(response.request)
            user_error.set({
                "code": 204,
                "message": "empty response"
            })
            logger_core.error("empty response")

            raise EmptyResponseException

        else:
            serialized_response = response.json()
            result = serialized_response.get("result")
            if result:
                user_id.set(user_tg_id)
                user_request.set(response.request)
                user_response.set(response)
                logger_core.info("user_info_request")
                return result
            else:
                error = serialized_response["error"]
                user_id.set(user_tg_id)
                user_request.set(response.request)
                user_error.set(error)

                if error["code"] == "rate_limit_exceeded":
                    logger_core.error("error")
                    raise RateLimitError(delay=error["delay"])

                elif error["message"] == "Application user error":
                    logger_core.error("error")
                    await del_token_from_cache(user_tg_id=user_tg_id)
                    raise ApplicationUserError

                elif error["message"] == "Internal server error":
                    logger_core.error("error")
                    await del_token_from_cache(user_tg_id=user_tg_id)
                    raise InternalServerError

                else:
                    logger_core.error("error")
                    raise ErrorResponseException
    return wrapper


def yookassa_json_api_serialization(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response, user_tg_id = await func(*args, **kwargs)
        user_id.set(user_tg_id)
        user_request.set(response.request)
        user_response.set(response)
        if response.status_code != 200:
            logger_payment.error("пришла ошибка от yookassa")
            raise PaymentError(msg_payment_error)

        response = response.json()
        logger_payment.info("платеж пользователя")

        return response

    return wrapper

