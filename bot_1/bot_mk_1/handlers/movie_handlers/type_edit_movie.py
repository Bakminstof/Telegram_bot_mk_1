from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp
from states.movie_states import MovieEditStates, MovieAddStates
from handlers.movie_handlers.review_movie import review_and_save_edited_movie
from keyboards.inline.movie_edit.ik_movie_edit import type_edit_keyboard, accept_keyboard
from keyboards.inline.movie_edit.callback_data_watch_edit import (
    callback_accept,
    callback_watch_edit,
    callback_type_edit
)


# type edit or rollback type edit `handler
@dp.callback_query_handler(
    callback_accept.filter(act='no'),
    state=[
        MovieEditStates.TypeEditState,
        MovieAddStates.TypeEditState
    ]
)
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='type'),
    state=[
        MovieEditStates.EditState,
        MovieAddStates.EditState
    ]
)
async def type_choice(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st in MovieAddStates.states_names:
        async with state.proxy() as data:
            name = data.get('new_movie').get('simple_name')

        await MovieAddStates.TypeEditState.set()
    else:
        async with state.proxy() as data:
            name = data.get('change_mv').get('simple_name')

        await MovieEditStates.TypeEditState.set()

    await call.message.edit_text('<i>{}</i>\nТип:'.format(name), reply_markup=type_edit_keyboard)


# film type `handler
@dp.callback_query_handler(
    callback_type_edit.filter(type='F'),
    state=[
        MovieEditStates.TypeEditState,
        MovieAddStates.TypeEditState
    ]
)
async def type_edit_f(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == MovieAddStates.TypeEditState.state:
        async with state.proxy() as data:
            name = data.get('new_movie').get('simple_name')
            data['new_movie']['type'] = 'Ф'
    else:
        async with state.proxy() as data:
            name = data.get('change_mv').get('simple_name')
            data['type'] = 'Ф'

    await call.message.edit_text('<i>{}</i>\nФильм, верно?'.format(name), reply_markup=accept_keyboard)


# serial type `handler
@dp.callback_query_handler(
    callback_type_edit.filter(type='S'),
    state=[
        MovieEditStates.TypeEditState,
        MovieAddStates.TypeEditState
    ]
)
async def type_edit_s(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == MovieAddStates.TypeEditState.state:
        async with state.proxy() as data:
            name = data.get('new_movie').get('simple_name')
            data['new_movie']['type'] = 'С'

    else:
        async with state.proxy() as data:
            name = data.get('change_mv').get('simple_name')
            data['type'] = 'С'

    await call.message.edit_text('<i>{}</i>\nСериал, верно?'.format(name), reply_markup=accept_keyboard)


# anime type `handler
@dp.callback_query_handler(
    callback_type_edit.filter(type='A'),
    state=[
        MovieEditStates.TypeEditState,
        MovieAddStates.TypeEditState
    ]
)
async def type_edit_a(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == MovieAddStates.TypeEditState.state:
        async with state.proxy() as data:
            name = data.get('new_movie').get('simple_name')
            data['new_movie']['type'] = 'А'

    else:
        async with state.proxy() as data:
            name = data.get('change_mv').get('simple_name')
            data['type'] = 'А'

    await call.message.edit_text('<i>{}</i>\nАниме, верно?'.format(name), reply_markup=accept_keyboard)


# accept type `handler
@dp.callback_query_handler(
    callback_accept.filter(act='yes'),
    state=[
        MovieEditStates.TypeEditState,
        MovieAddStates.TypeEditState
    ]
)
async def type_edit_accept(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == MovieEditStates.TypeEditState.state:
        async with state.proxy() as data:
            type_ = data.pop('type')
            data['change_mv']['type'] = type_
        await MovieEditStates.EditState.set()
    else:
        await MovieAddStates.EditState.set()

    await review_and_save_edited_movie(state=state, call=call, name_st=st)
