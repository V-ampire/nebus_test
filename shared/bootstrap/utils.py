import traceback
from functools import wraps


def str_exception(exc: Exception, with_traceback=True) -> str:
    try:
        message = f"{type(exc)}: {str(exc)}."
    except Exception as e:
        message = (f"{type(exc)}: "
                   f"<Error when converting an exception to the line: {e}>")
    if with_traceback:
        traceback_str = ''.join(traceback.format_tb(exc.__traceback__))
        message = f"{message}\n{traceback_str}"
    return message


def type_exc(exc: Exception) -> str:
    return exc.__class__.__name__


def log_no_raise(logger):
    def _deco(func):
        @wraps(func)
        async def _wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                logger.error(str_exception(exc))
        return _wrapper
    return _deco
