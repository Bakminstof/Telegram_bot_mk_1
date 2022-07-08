import logging.config

from os.path import isfile, realpath

from data.config import MAIN_DB
from utils.misc.logs.logger import dict_config, logger_decorator
from main_db.main_db_orm.mian_db_schema import Base, engine_main

logging.config.dictConfig(dict_config)
init_main_dblogger = logging.getLogger('init_main_db')


@logger_decorator(init_main_dblogger)
async def init_main_db() -> None:
    db = realpath('{}'.format(MAIN_DB))

    if not isfile(db):
        async with engine_main.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            init_main_dblogger.info('Init main db')

            await engine_main.dispose()
