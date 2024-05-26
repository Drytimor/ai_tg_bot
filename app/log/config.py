from httpx import Response, Request
import logging
from contextvars import ContextVar
from logging.config import dictConfig


def filter_level_maker(level):
    level = getattr(logging, level)

    def filter(record):
        return record.levelno <= level

    return filter


user_id: ContextVar[int] = ContextVar("user_id")
user_request: ContextVar["Request"] = ContextVar("user_request")
user_response: ContextVar["Response"] = ContextVar("user_response")
user_error: ContextVar[dict] = ContextVar("user_error")
user_payment: ContextVar[dict] = ContextVar("user_payment")


class RequestCoreInfoFilter(logging.Filter):

    def filter(self, record):
        record.user_id = user_id.get()
        request = user_request.get()
        record.request_url = request.url
        record.request_method = request.method
        record.request_content = request.content
        response = user_response.get()
        record.response_status_code = response.status_code
        record.response_content = response.content
        return True


class RequestCoreErrorFilter(logging.Filter):

    def filter(self, record):
        record.user_id = user_id.get()
        request = user_request.get()
        error = user_error.get()
        record.request_url = request.url
        record.request_method = request.method
        record.request_content = request.content
        record.error_status = error.get("status")
        record.error_code = error.get("code")
        record.error_message = error.get("message")
        return True


class WebhookPayment(logging.Filter):
    def filter(self, record):
        pass


fmt_user_info = (
    "[%(asctime)s] %(levelname)s user_id:%(user_id)s"
    "\nRequest:'%(request_method)s %(request_url)s content:%(request_content)s'"
    "\nResponse:%(response_status_code)s content:%(response_content)s\n"
)
fmt_user_error = (
    "[%(asctime)s] %(levelname)s user_id:%(user_id)s"
    "\nRequest:'%(request_method)s %(request_url)s content:%(request_content)s'"
    "\nError:%(error_status)s code:%(error_code)s message:%(error_message)s\n"
)

logging_config = {
    "version": 1,
    "filters": {
        "filter_info": {
            "()": filter_level_maker,
            "level": "INFO"
        },
        "request_info": {
            "()": RequestCoreInfoFilter
        },
        "request_error": {
            "()": RequestCoreErrorFilter
        },
    },
    "formatters": {
        "simple": {
            "format": "%(levelname)s: [%(asctime)s] %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "user_info": {
            "format": fmt_user_info,
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "user_error": {
            "format": fmt_user_error,
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
    },
    "handlers": {
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["default", "file_dev", "file_core_info", "file_core_error"]
        },
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
            "level": "INFO"
        },
        "file_dev": {
            "class": "logging.FileHandler",
            "formatter": "simple",
            "filename": "app/log/log.log",
            "level": "INFO"
        },
        "file_core_info": {
            "class": "logging.FileHandler",
            "formatter": "user_info",
            "filters": ["filter_info", "request_info"],
            "filename": "app/log/core_info_http.log",
            "level": "INFO"
        },
        "file_core_error": {
            "class": "logging.FileHandler",
            "formatter": "user_error",
            "filters": ["request_error"],
            "filename": "app/log/core_error_http.log",
            "level": "ERROR"
        },
        "file_payment_error": {
            "class": "logging.FileHandler",
            "formatter": "user_info",
            "filters": ["request_info"],
            "filename": "app/log/core_error_http.log",
            "level": "ERROR"
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": 'INFO',
        },
        "core_api": {
            "handlers": ["file_core_info", "file_core_error"],
            "level": "INFO",
        },
        "payment": {
            "handlers": ["file_core_info", "file_payment_error"],
            "level": "INFO",
        },
        "raw_exception": {
            "handlers": ["file_dev"],
            "level": "ERROR"
        },
        "httpx": {
            "handlers": ["file_dev"],
            "level": "INFO",
        },
        "sqlalchemy": {
            "handlers": ["file_dev"],
            "level": "INFO",
        },
        "aiogram": {
            "handlers": ["file_dev"],
            "level": "INFO",
        }
    }
}


dictConfig(logging_config)
queue_handler = logging.getHandlerByName("queue_handler")


logger_core = logging.getLogger("core_api")
logger_payment = logging.getLogger("payment")
logger_raw_exc = logging.getLogger("raw_exception")
