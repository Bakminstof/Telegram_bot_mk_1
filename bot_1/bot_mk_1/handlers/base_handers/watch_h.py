import logging.config

from typing import List
from aiogram import types
from sqlalchemy import select
from collections import OrderedDict
from aiogram.dispatcher import FSMContext

from loader import dp
from data.config import yes, no, format_movie_name_pattern
from utils.misc.logs.logger import dict_config
from states.movie_states import MovieEditStates, MovieAddStates
from main_db.main_db_orm.mian_db_schema import a_session_main, WatchTable
from keyboards.inline.movie_list.ik_movies_list import watch_list_keyboard, watch_add_keyboard

logging.config.dictConfig(dict_config)
watch_logger = logging.getLogger('watch')


async def get_movie_list(message: types.Message):
    stmt = select(WatchTable.id, WatchTable.name, WatchTable.type, WatchTable.watched). \
        filter(WatchTable.user_id.is_(message.from_user.id))

    res = await a_session_main.execute(stmt)
    watched: List[tuple] | List[None] = res.all()

    if watched:
        watch_logger.info('Completing list')

        watched_movies = OrderedDict(
            {
                i + 1: {
                    'id_in_db': movie[0],
                    'simple_name': movie[1],
                    'type': movie[2],
                    'status': movie[3],
                    'format_name': format_movie_name_pattern.format(
                        # todo настроить ссылку <a href="https://google.com/serach={n}">{n}</a>
                        n=movie[1],  # name
                        t=movie[2],  # type
                        c=yes if movie[3] else no  # status
                    )
                }
                for i, movie in enumerate(watched)
            }
        )
        return watched_movies
    else:
        return OrderedDict()


@dp.message_handler(commands=['watch'], state=None)
async def watch(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        movies = data.get('movies')

    if movies:
        watch_logger.info('Using cash')

        msg = '<i>Мой список</i>:\n' + '\n'.join(map(lambda x: x.get('format_name'), movies.values()))

        await message.answer(msg, reply_markup=watch_list_keyboard)
        await MovieEditStates.ChangeState.set()

    else:
        watch_logger.info('Using DB')

        watched = await get_movie_list(message)

        async with state.proxy() as data:
            data['movies'] = watched

        if watched:
            msg = '<i>Мой список</i>:\n' + '\n'.join(map(lambda x: x.get('format_name'), watched.values()))
            await MovieEditStates.ChangeState.set()
            await message.answer(msg, reply_markup=watch_list_keyboard)

        else:
            await MovieAddStates.AddMovieState.set()
            await message.answer('Ваш список пуст', reply_markup=watch_add_keyboard)
