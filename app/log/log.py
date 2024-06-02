import logging
from functools import wraps
from app.services.cache import (
    del_token_from_cache,
    set_context_limit_in_cache
)
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


class ContextLimitError(Exception):
    """Превышен предельный лимит контекста"""


class PaymentError(Exception):
    """Пришла ошибка от yookassa"""
    def __init__(self, msg=None):
        self.msg = msg


class NegativeBalance(Exception):
    """Отрицательный баланс пользователя"""


msg_error_answer = """
Возникла непредвиденная ошибка.\nОбратитесь в техническую поддержку\nили попробуйте перезапустить бота командой /start
"""
msg_limit_error = """
Невозможно обработать запрос из-за высокой нагрузки. Пожалуйста, попробуйте повторить запрос через %d сек
"""
msg_limit_context_error = """
Лимит запросов превышен.\nДля продолжения необходимо сбросить контекст командой /context и начать беседу с новой темы
"""
msg_server_error = "error %s"
msg_payment_error = "Невозможно провести оплату"


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
                    logger_core.error("rate_limit_exceeded")
                    raise RateLimitError(delay=error["delay"])

                elif error["code"] == "context_limit_exceeded":
                    await set_context_limit_in_cache(user_tg_id, value=0)
                    logger_core.error("context_limit_exceeded")
                    raise ContextLimitError

                elif error["message"] == "Application user error":
                    await del_token_from_cache(user_tg_id=user_tg_id)
                    logger_core.error("Application user error")
                    raise ApplicationUserError

                elif error["message"] == "Internal server error":
                    await del_token_from_cache(user_tg_id=user_tg_id)
                    logger_core.error("Internal server error")
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

