from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp
from states.movie_states import MovieEditStates, MovieAddStates
from handlers.movie_handlers.review_movie import review_and_save_edited_movie
from keyboards.inline.movie_edit.ik_movie_edit import watched_keyboard
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_watch_edit


# status edit `handler
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='status'),
    state=[
        MovieEditStates.EditState,
        MovieAddStates.EditState
    ]
)
async def status_edit(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == MovieAddStates.EditState.state:
        async with state.proxy() as data:
            name = data.get('new_movie').get('simple_name')
            await MovieAddStates.StatusEditState.set()
    else:
        async with state.proxy() as data:
            name = data.get('change_mv').get('simple_name')
            await MovieEditStates.StatusEditState.set()

    await call.message.edit_text('<i>{}</i>:'.format(name), reply_markup=watched_keyboard)


# status accept `handler
@dp.callback_query_handler(
    state=[
        MovieEditStates.StatusEditState,
        MovieAddStates.StatusEditState
    ]
)
async def status_edit_accept(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if call.data.split(':')[1] == 'yes':
        status_ = True
    else:
        status_ = False

    if st == MovieAddStates.StatusEditState.state:
        async with state.proxy() as data:
            data['new_movie']['status'] = status_

    else:
        async with state.proxy() as data:
            data['change_mv']['status'] = status_

    await review_and_save_edited_movie(state=state, call=call, name_st=st)
