from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext

from loader import dp
from states.channel_states import ChannelAddStates, ChannelEditStates
from keyboards.inline.movie_edit.ik_movie_edit import accept_keyboard
from handlers.channel_subscriptions.review_subs import review_channel
from keyboards.inline.movie_list.callback_data_watch_list import callback_watch_list
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_watch_edit, callback_accept


# add new channel `handler
@dp.callback_query_handler(callback_watch_list.filter(change='add'),
                           state=[ChannelEditStates.EditState, ChannelAddStates.ChangeState])
async def init_name(call: CallbackQuery):
    await call.message.edit_text('Введите название', reply_markup=None)
    await ChannelAddStates.EditNameState.set()


# init channel name `handler
@dp.message_handler(state=ChannelAddStates.EditNameState)
async def edit_name_subscription(message: Message, state: FSMContext):
    async with state.proxy() as data:
        check = len(data.get('subscriptions', {}))

        data['channel_add'] = {
            'id': check + 1 if check else 1,
            'custom_name': message.text,
        }

    await message.answer('Вставьте ссылку на канал')
    await ChannelAddStates.EditUrlState.set()


# edit name or rollback name edit `handler
@dp.callback_query_handler(
    callback_accept.filter(act='no'),
    state=[
        ChannelAddStates.EditNameState,
        ChannelEditStates.EditNameState
    ]
)
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='name'),
    state=[
        ChannelAddStates.EditState,
        ChannelEditStates.EditState
    ]
)
async def name_edit(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st in ChannelAddStates.states_names:
        async with state.proxy() as data:
            name = data.get('channel_add').get('custom_name')

        await ChannelAddStates.EditNameState2.set()

    else:
        async with state.proxy() as data:
            name = data.get('channel_edit').get('custom_name')

        await ChannelEditStates.EditNameState.set()

    await call.message.edit_text('<i>{}</i>:\nВведите новое название'.format(name))


# review change name `handler
@dp.message_handler(state=[ChannelEditStates.EditNameState, ChannelAddStates.EditNameState2])
async def name_change(message: Message, state: FSMContext):
    st = await state.get_state()

    if st == ChannelAddStates.EditNameState2.state:
        async with state.proxy() as data:
            data['c_name'] = message.text
            old_name = data.get('channel_add').get('custom_name')
            new_name = data.get('c_name')

            await ChannelAddStates.EditNameState.set()
    else:
        async with state.proxy() as data:
            data['c_name'] = message.text
            old_name = data.get('channel_edit').get('custom_name')
            new_name = data.get('c_name')

            await ChannelEditStates.EditNameState.set()

    await message.answer(
        '<i>{old}</i>\nНовое имя:\n<b>{new}</b>'.format(old=old_name, new=new_name),
        reply_markup=accept_keyboard
    )


# accept name `handler
@dp.callback_query_handler(
    callback_accept.filter(act='yes'),
    state=[
        ChannelEditStates.EditNameState,
        ChannelAddStates.EditNameState
    ]
)
async def name_edit_accept(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == ChannelAddStates.EditNameState.state:
        async with state.proxy() as data:
            name_ = data.pop('c_name')
            data['channel_add']['custom_name'] = name_
    else:
        async with state.proxy() as data:
            name_ = data.pop('c_name')
            data['channel_edit']['custom_name'] = name_

    await review_channel(state=state, message=call.message, name_st=st)
