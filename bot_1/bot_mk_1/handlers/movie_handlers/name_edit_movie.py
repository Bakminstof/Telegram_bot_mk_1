from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext

from loader import dp
from states.movie_states import MovieAddStates, MovieEditStates
from handlers.movie_handlers.review_movie import review_and_save_edited_movie
from keyboards.inline.movie_edit.ik_movie_edit import type_edit_keyboard, accept_keyboard
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_accept, callback_watch_edit
from keyboards.inline.movie_list.callback_data_watch_list import callback_watch_list


# add new movie `handler
@dp.callback_query_handler(callback_watch_list.filter(change='add'),
                           state=[MovieEditStates.EditState, MovieAddStates.AddMovieState])
async def add_movie(call: CallbackQuery):
    await call.message.edit_text('Введите название', reply_markup=None)
    await MovieAddStates.AddMovieState.set()


# init movie name `handler
@dp.message_handler(state=MovieAddStates.AddMovieState)
async def def_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        check = len(data.get('movies', {}))

        data['new_movie'] = {
            'id': check + 1 if check else 1,
            'simple_name':  message.text,
        }
        name = data.get('new_movie').get('simple_name')

    await message.answer('<b>{}</b>\nТип:'.format(name), reply_markup=type_edit_keyboard)
    await MovieAddStates.TypeEditState.set()


# edit name or rollback name edit `handler
@dp.callback_query_handler(
    callback_accept.filter(act='no'),
    state=[
        MovieEditStates.NameEditState,
        MovieAddStates.NameEditState
    ]
)
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='name'),
    state=[
        MovieEditStates.EditState,
        MovieAddStates.EditState
    ]
)
async def name_edit(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st in MovieAddStates.states_names:
        async with state.proxy() as data:
            name = data.get('new_movie').get('simple_name')

        await MovieAddStates.NameEditState.set()

    else:
        async with state.proxy() as data:
            name = data.get('change_mv').get('simple_name')

        await MovieEditStates.NameEditState.set()

    await call.message.edit_text('<i>{}</i>:\nВведите новое название'.format(name))


# review change name `handler
@dp.message_handler(state=[MovieEditStates.NameEditState, MovieAddStates.NameEditState])
async def name_edit(message: Message, state: FSMContext):
    st = await state.get_state()

    if st == MovieAddStates.NameEditState.state:
        async with state.proxy() as data:
            data['name'] = message.text
            old_name = data.get('new_movie').get('simple_name')
            new_name = data.get('name')
    else:
        async with state.proxy() as data:
            data['name'] = message.text
            old_name = data.get('change_mv').get('simple_name')
            new_name = data.get('name')

    await message.answer(
        '<i>{old}</i>\nНовое имя:\n<b>{new}</b>'.format(old=old_name, new=new_name),
        reply_markup=accept_keyboard
    )


# accept name `handler
@dp.callback_query_handler(
    callback_accept.filter(act='yes'),
    state=[
        MovieEditStates.NameEditState,
        MovieAddStates.NameEditState
    ]
)
async def name_edit_accept(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == MovieAddStates.NameEditState.state:
        async with state.proxy() as data:
            name_ = data.pop('name')
            data['new_movie']['simple_name'] = name_
    else:
        async with state.proxy() as data:
            name_ = data.pop('name')
            data['change_mv']['simple_name'] = name_

    await review_and_save_edited_movie(state=state, call=call, name_st=st)
