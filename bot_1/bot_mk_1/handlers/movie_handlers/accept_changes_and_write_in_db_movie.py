import logging.config

from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp
from utils.misc.logs.logger import dict_config
from states.movie_states import MovieEditStates, MovieAddStates
from handlers.base_handers.watch_h import get_movie_list
from main_db.main_db_orm.mian_db_schema import WatchTable, a_session_main
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_accept

logging.config.dictConfig(dict_config)
movie_write_in_db_logger = logging.getLogger('movie_write_in_db')


# write all changes into db `handler
@dp.callback_query_handler(
    callback_accept.filter(act='save_all'),
    state=[
        MovieEditStates.EditState,
        MovieAddStates.EditState
    ]
)
async def write_all_changes_into_db(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text('Принято ;)', reply_markup=None)

    async with state.proxy() as data:
        to_update = data.get('update', {}).values()
        to_save = data.get('save', {}).values()

        data.pop('change_mv')
        data.pop('new_movie')
        data.pop('update')
        data.pop('save')

    if to_save:
        save = [
            WatchTable(
                name=movie.get('simple_name'),
                type=movie.get('type'),
                watched=movie.get('status'),
                user_id=call.from_user.id
            ) for movie in to_save
        ]

        movie_write_in_db_logger.info(
            'Saved: {}'.format(
                ', '.join(
                    [
                        movie.get('simple_name')
                        for movie in to_save
                    ]
                )
            )
        )

        a_session_main.add_all(save)
        await a_session_main.commit()

    if to_update:
        update = [
            {
                'id': movie.get('id_in_db'),
                'name': movie.get('simple_name'),
                'type': movie.get('type'),
                'watched': movie.get('status'),
                'user_id': call.from_user.id
            } for movie in to_update
        ]

        movie_write_in_db_logger.info(
            'Updated: {}'.format(
                ', '.join(
                    [
                        movie.get('name')
                        for movie in update
                    ]
                )
            )
        )

        await a_session_main.run_sync(lambda session: session.bulk_update_mappings(WatchTable, update))
        await a_session_main.commit()

    movie_write_in_db_logger.warning('Accept changes')

    await call.message.edit_text('Сохранено!')
    await state.reset_state(with_data=False)

    movie = await get_movie_list(call.message)

    async with state.proxy() as data:
        data['movie'] = movie
