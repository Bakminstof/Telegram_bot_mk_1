import functools
import logging.config

from typing import Callable
from logging import Logger

from loader import DEBUG
from utils.misc.logs.logger import dict_config

logging.config.dictConfig(dict_config)
BASE_LOGGER = logging.getLogger('BASE_DEBUG_LOGGER')


def logger_decorator(logger: Logger = None):
    if not logger:
        logger = BASE_LOGGER

    def __decorator(func: Callable):
        @functools.wraps(func)
        async def __wrap(*args, **kwargs):
            if DEBUG:
                try:
                    logger.debug('Start func: <{}>'.format(func.__name__))

                    res = await func(*args, **kwargs)

                    logger.debug('End func: <{}>'.format(func.__name__))

                    return res

                except Exception as ex:
                    logger.exception('Exception in func: <{n}>\n{ex}'.format(n=func.__name__, ex=ex))
                    raise
            else:
                return await func(*args, **kwargs)

        return __wrap

    return __decorator
