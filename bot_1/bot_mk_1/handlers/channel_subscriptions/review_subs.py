import logging.config

from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext

from loader import dp
from data.config import format_channel_name_pattern
from utils.misc.logs.logger import dict_config
from states.channel_states import ChannelAddStates, ChannelEditStates
from keyboards.inline.movie_edit.ik_movie_edit import edit_movies_list_keyboard, sub_edit_keyboard
from keyboards.inline.movie_list.ik_movies_list import watch_add_keyboard
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_watch_edit
from keyboards.inline.movie_list.callback_data_watch_list import callback_watch_list

logging.config.dictConfig(dict_config)
subscription_review_logger = logging.getLogger('subscription_review')


# list of subscriptions for change with /№ `handler
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='back'),
    state=[
        ChannelAddStates.EditState,
        ChannelEditStates.EditState
    ]
)
@dp.callback_query_handler(callback_watch_list.filter(change='yes'),
                           state=ChannelEditStates.ChangeState)
async def review_subscriptions(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        subscriptions = data.get('subscriptions')

    list_subscriptions = '\n'.join(
            map(
                lambda x: '/{i}: {v}'.format(i=x[0], v=x[1].get('format_name')), subscriptions.items()
            )
        )

    if list_subscriptions:
        await ChannelEditStates.EditState.set()
        await call.message.edit_text(
            list_subscriptions,
            reply_markup=edit_movies_list_keyboard
        )

    else:
        await ChannelAddStates.ChangeState.set()
        await call.message.answer('Ваш список пуст', reply_markup=watch_add_keyboard)


# personal review channel for edit `handler
@dp.message_handler(state=ChannelEditStates.EditState)
async def personal_review(message: Message, state: FSMContext):
    comm = message.text

    try:
        comm = int(comm[1:])

        async with state.proxy() as data:
            subscriptions = data.get('subscriptions')

        if comm in subscriptions.keys():
            async with state.proxy() as data:
                data['channel_edit'] = subscriptions.get(comm)
                data['channel_edit']['id'] = comm

            await message.answer(subscriptions.get(comm).get('format_name'), reply_markup=sub_edit_keyboard)

    except (IndexError, ValueError) as e:
        subscription_review_logger.exception(e)
        await message.answer('Не понимаю :/')


# review edited channel
async def review_channel(message: Message, state: FSMContext, name_st: str):
    if name_st in ChannelAddStates.all_states_names:
        subscription_name = 'channel_add'
        await ChannelAddStates.EditState.set()

    else:
        subscription_name = 'channel_edit'
        await ChannelEditStates.EditState.set()

    async with state.proxy() as data:
        id_ = data.get(subscription_name).get('id')
        custom_name_ = data.get(subscription_name).get('custom_name')

        sub = data.get(subscription_name)

        format_name_ = format_channel_name_pattern.format(n=custom_name_)

        data[subscription_name]['format_name'] = format_name_
        updated_sub = data.get('subscriptions', {}).get(id_, {})
        updated_sub.update(sub)

        if subscription_name == 'channel_add':
            save = data.get('save', {})
            save[id_] = updated_sub
            data['save'] = save
        else:
            update = data.get('update', {})
            update[id_] = updated_sub
            data['update'] = update

        data['subscriptions'][id_] = updated_sub

        await message.answer(format_name_, reply_markup=sub_edit_keyboard)
