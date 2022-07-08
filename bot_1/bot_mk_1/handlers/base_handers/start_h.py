import datetime
import logging.config

from aiogram import types
from sqlalchemy import select

from loader import dp
from utils.misc.logs.logger import dict_config
from main_db.main_db_orm.mian_db_schema import a_session_main, UsersTable

logging.config.dictConfig(dict_config)
start_logger = logging.getLogger('start')


@dp.message_handler(commands=['start'], state=None)
async def start(message: types.Message):
    stmt = select(UsersTable).filter(UsersTable.telegram_id.is_(message.from_user.id))

    res = await a_session_main.execute(stmt)
    check = res.one_or_none()

    if not check:
        new_user = UsersTable(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            date_first_auth=datetime.datetime.now()
        )
        a_session_main.add(new_user)
        await a_session_main.commit()

        start_logger.info('Добавлен новый пользователь: {}'.format(message.from_user.first_name))

    await message.answer('Привет, {}!'.format(message.from_user.first_name))
