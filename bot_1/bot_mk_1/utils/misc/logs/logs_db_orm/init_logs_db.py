import logging.config

from os.path import isfile, realpath

from data.config import LOGS_DB
from utils.misc.logs.logger import dict_config, logger_decorator
from utils.misc.logs.logs_db_orm.logs_schema import Base, engine_log

logging.config.dictConfig(dict_config)
init_logs_dblogger = logging.getLogger('init_logs_db')


@logger_decorator(init_logs_dblogger)
async def init_logs_db() -> None:
    db = realpath('{}'.format(LOGS_DB))

    if not isfile(db):
        async with engine_log.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            init_logs_dblogger.info('init logs db')

        await engine_log.dispose()
