import logging.config

from typing import Dict
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext

from loader import dp
from data.config import format_movie_name_pattern, no, yes
from utils.misc.logs.logger import dict_config
from states.movie_states import MovieEditStates, MovieAddStates
from handlers.base_handers.watch_h import watch_logger
from keyboards.inline.movie_edit.ik_movie_edit import edit_movies_list_keyboard, movie_edit_keyboard
from keyboards.inline.movie_list.ik_movies_list import watch_add_keyboard
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_watch_edit
from keyboards.inline.movie_list.callback_data_watch_list import callback_watch_list

logging.config.dictConfig(dict_config)
review_movie_logger = logging.getLogger('review_movie')


# list of movie for change with /№ `handler
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='back'),
    state=[
        MovieEditStates.EditState,
        MovieAddStates.EditState
    ]
)
@dp.callback_query_handler(callback_watch_list.filter(change='yes'),
                           state=MovieEditStates.ChangeState)
async def watch_list_change_yes(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        movies: Dict[int: Dict[str: str | int]] = data.get('movies')

    list_movies = '\n'.join(
            map(
                lambda x: '/{i}: {v}'.format(i=x[0], v=x[1].get('format_name')), movies.items()
            )
        )
    if list_movies:
        await MovieEditStates.EditState.set()
        await call.message.edit_text(
            list_movies,
            reply_markup=edit_movies_list_keyboard
        )
    else:
        watch_logger.info('empty list')

        await call.message.delete()
        await MovieAddStates.AddMovieState.set()
        await call.message.answer('Ваш список пуст', reply_markup=watch_add_keyboard)


# personal review movie for edit `handler
@dp.message_handler(state=MovieEditStates.EditState)
async def review(message: Message, state: FSMContext):
    comm = message.text

    try:
        comm = int(comm[1:])

        async with state.proxy() as data:
            movies: Dict[int: Dict[str: str | int]] = data.get('movies')

        if comm in movies.keys():
            async with state.proxy() as data:
                data['change_mv'] = movies.get(comm)
                data['change_mv']['id'] = comm

            await message.answer(movies.get(comm).get('simple_name'), reply_markup=movie_edit_keyboard)

    except (IndexError, ValueError) as e:
        review_movie_logger.exception(e)
        await message.answer('Не понимаю :/')


# review edited movie
async def review_and_save_edited_movie(call: CallbackQuery, state: FSMContext, name_st: str):
    if name_st in MovieAddStates.all_states_names:
        mov_name = 'new_movie'
        await MovieAddStates.EditState.set()

    else:
        mov_name = 'change_mv'
        await MovieEditStates.EditState.set()

    async with state.proxy() as data:
        id_ = data.get(mov_name).get('id')
        name_ = data.get(mov_name).get('simple_name')
        type_ = data.get(mov_name).get('type')
        status_ = data.get(mov_name).get('status')

        mv = data.get(mov_name)

        format_name_ = format_movie_name_pattern.format(
            n=name_,
            t=type_,
            c=yes if status_ else no
        )

        data[mov_name]['format_name'] = format_name_
        updated_mv = data.get('movies', {}).get(id_, {})
        updated_mv.update(mv)

        if mov_name == 'new_movie':
            save: Dict[int: Dict | None] = data.get('save', {})
            save[id_] = updated_mv
            data['save'] = save
        else:
            update: Dict[int: Dict | None] = data.get('update', {})
            update[id_] = updated_mv
            data['update'] = update

        data['movies'][id_] = updated_mv

    await call.message.edit_text('Принято ;)', reply_markup=None)
    await call.message.delete()
    await call.message.answer(format_name_, reply_markup=movie_edit_keyboard)
