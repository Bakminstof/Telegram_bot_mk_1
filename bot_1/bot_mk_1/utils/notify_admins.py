import logging.config

from asyncio import gather
from aiogram import Dispatcher

from data.config import ADMINS
from utils.misc.logs.logger import dict_config
from main_db.main_db_orm.init_main_db import init_main_db
from main_db.main_db_orm.mian_db_schema import a_session_main, engine_main
from utils.misc.logs.logs_db_orm.logs_schema import a_session_log, engine_log
from utils.misc.logs.logs_db_orm.init_logs_db import init_logs_db

logging.config.dictConfig(dict_config)
notify_logger = logging.getLogger('notify')


async def _graceful_stop():
    notify_logger.info('Graceful stopping ...')

    await a_session_log.commit()
    await a_session_main.commit()

    await a_session_log.close()
    await a_session_main.close()

    await engine_main.dispose()
    await engine_log.dispose()


async def on_startup_notify(dp: Dispatcher):
    await init_logs_db()
    await init_main_db()

    message = 'Бот Запущен'
    tasks = [dp.bot.send_message(admin, "<b>{}</b>".format(message)) for admin in ADMINS]

    notify_logger.info(message)
    await gather(*tasks)


async def on_shutdown(dp: Dispatcher):
    message = 'Бот завершил работу'
    tasks = [dp.bot.send_message(admin, "<b>{}</b>".format(message)) for admin in ADMINS]

    notify_logger.info(message)

    await gather(*tasks)
    await _graceful_stop()
