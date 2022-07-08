import logging.config

from sqlalchemy import delete
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from handlers.movie_handlers.review_movie import review_and_save_edited_movie
from loader import dp
from utils.misc.logs.logger import dict_config
from states.movie_states import MovieEditStates, MovieAddStates
from main_db.main_db_orm.mian_db_schema import a_session_main, WatchTable
from keyboards.inline.movie_edit.ik_movie_edit import accept_keyboard, back_keyboard
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_watch_edit, callback_accept

logging.config.dictConfig(dict_config)
delete_mov_dblogger = logging.getLogger('delete_mov')


# init delete `handler
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='del'),
    state=[
        MovieEditStates.EditState,
        MovieAddStates.EditState
    ]
)
async def delete_movie(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == MovieAddStates.EditState.state:
        mv = 'new_movie'
        await MovieAddStates.DeleteState.set()
    else:
        mv = 'change_mv'
        await MovieEditStates.DeleteState.set()

    async with state.proxy() as data:
        format_name_movie = data.get(mv).get('format_name')

    await call.message.edit_text('Удалить:\n{}'.format(format_name_movie), reply_markup=accept_keyboard)


# accept delete `handler
@dp.callback_query_handler(
    callback_accept.filter(act='yes'),
    state=[
        MovieEditStates.DeleteState,
        MovieAddStates.DeleteState
    ]
)
async def act_delete(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == MovieAddStates.DeleteState.state:
        mv = 'new_movie'
    else:
        mv = 'change_mv'

    async with state.proxy() as data:
        id_ = data.get(mv).get('id')
        id_in_db_ = data.get(mv).get('id_in_db')
        format_name_movie = data.get(mv).get('format_name')
        simple_name = data.get(mv).get('simple_name')

        data.get('movies').pop(id_)

        movies = data.get('movies')

        reassembled_movies = {
            key + 1: val
            for key, val in enumerate(movies.values())
        }

        data['movies'] = reassembled_movies

    stmt = delete(WatchTable).filter(WatchTable.id.is_(id_in_db_))

    await a_session_main.execute(stmt)

    delete_mov_dblogger.info('Добавлено для удаления: "{}"'.format(simple_name))

    await call.message.edit_text('{}\n<b><i>Удалено</i></b>'.format(format_name_movie), reply_markup=back_keyboard)
    await MovieEditStates.EditState.set()


# no delete `handler
@dp.callback_query_handler(
    callback_accept.filter(act='no'),
    state=[
        MovieEditStates.DeleteState,
        MovieAddStates.DeleteState
    ]
)
async def den_delete(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()
    await review_and_save_edited_movie(state=state, call=call, name_st=st)
