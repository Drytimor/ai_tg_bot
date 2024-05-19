from httpx import Response, Request
import logging
from contextvars import ContextVar
from logging.config import dictConfig


# 'propagate': False
def filter_level_maker(level):
    level = getattr(logging, level)

    def filter(record):
        return record.levelno <= level

    return filter


user_id: ContextVar[int] = ContextVar("user_id")
user_request: ContextVar["Request"] = ContextVar("user_request")
user_response: ContextVar["Response"] = ContextVar("user_response")
user_error: ContextVar[dict] = ContextVar("user_error")


class RequestInfoFilter(logging.Filter):

    def filter(self, record):
        record.user_id = user_id.get()
        request = user_request.get()
        record.request_url = request.url
        record.request_method = request.method
        record.request_content = request.content
        # record.request_headers = request.headers
        response = user_response.get()
        record.response_status_code = response.status_code
        record.response_content = response.content

        return True


class RequestErrorFilter(logging.Filter):

    def filter(self, record):
        record.user_id = user_id.get()
        request = user_request.get()
        error = user_error.get()
        record.request_url = request.url
        record.request_method = request.method
        record.request_content = request.content
        # record.request_headers = request.headers
        record.error_status = error.get("status")
        record.error_code = error.get("code")
        record.error_message = error.get("message")
        return True


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
            "()": RequestInfoFilter
        },
        "request_error": {
            "()": RequestErrorFilter
        }
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
        }
    },
    "handlers": {
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["default", "file_dev", "file_core_info", "file_core_error"]
        },
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
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
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": 'INFO',
        },
        "log": {
            "handlers": ["file_core_info", "file_core_error"],
            "level": "INFO"
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
logger = logging.getLogger("log")
queue_handler = logging.getHandlerByName("queue_handler")

"""
class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        my_context = kwargs.pop('id', self.extra['id'])
        return 'id=%s %s' % (my_context, msg), kwargs
fmt = logging.Formatter("%(levelname)s: [%(asctime)s] %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

logger.setLevel(logging.INFO)

file_handler_info = logging.FileHandler("app/log/core_info_http.log")
file_handler_info.setLevel(logging.INFO)
file_handler_info.setFormatter(fmt)
file_handler_info.addFilter(filter_maker("INFO"))

file_handler_error = logging.FileHandler("app/log/core_error_http.log")
file_handler_error.setLevel(logging.ERROR)
file_handler_error.setFormatter(fmt)

logger.addHandler(file_handler_info)
logger.addHandler(file_handler_error)

que = queue.Queue()
queue_handler = QueueHandler(que)
logger.addHandler(queue_handler)

listener = QueueListener(
    que, file_handler_error, file_handler_info, respect_handler_level=True,
)
"""
