import logging.config

from sqlalchemy import delete
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp
from utils.misc.logs.logger import dict_config
from states.channel_states import ChannelAddStates, ChannelEditStates
from main_db.main_db_orm.mian_db_schema import a_session_main, SubscriptionsTable
from keyboards.inline.movie_edit.ik_movie_edit import accept_keyboard, back_keyboard
from handlers.channel_subscriptions.review_subs import review_channel
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_watch_edit, callback_accept


logging.config.dictConfig(dict_config)
delete_subs_logger = logging.getLogger('delete_subs')


# init delete `handler
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='del'),
    state=[
        ChannelAddStates.EditState,
        ChannelEditStates.EditState
    ]
)
async def delete_movie(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == ChannelAddStates.EditState.state:
        sub = 'channel_add'
        await ChannelAddStates.DeleteState.set()
    else:
        sub = 'channel_edit'
        await ChannelEditStates.DeleteState.set()

    async with state.proxy() as data:
        format_name_movie = data.get(sub).get('format_name')

    await call.message.edit_text('Удалить:\n{}'.format(format_name_movie), reply_markup=accept_keyboard)


# accept delete `handler
@dp.callback_query_handler(
    callback_accept.filter(act='yes'),
    state=[
        ChannelEditStates.DeleteState,
        ChannelAddStates.DeleteState
    ]
)
async def act_delete(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == ChannelAddStates.DeleteState.state:
        sub = 'channel_add'
    else:
        sub = 'channel_edit'

    async with state.proxy() as data:
        id_ = data.get(sub).get('id')
        id_in_db_ = data.get(sub).get('id_in_db')
        format_name_sub = data.get(sub).get('format_name')
        custom_name = data.get(sub).get('custom_name')

        data.get('subscriptions').pop(id_)

        subscriptions = data.get('subscriptions')

        reassembled_subscriptions = {
            key + 1: val
            for key, val in enumerate(subscriptions.values())
        }

        data['subscriptions'] = reassembled_subscriptions

    stmt = delete(SubscriptionsTable).filter(SubscriptionsTable.id.is_(id_in_db_))

    await a_session_main.execute(stmt)

    delete_subs_logger.info('Deleted: "{}"'.format(custom_name))

    await call.message.edit_text('{}\n<b><i>Удалено</i></b>'.format(format_name_sub), reply_markup=back_keyboard)
    await ChannelEditStates.EditState.set()


# no delete `handler
@dp.callback_query_handler(
    callback_accept.filter(act='no'),
    state=[
        ChannelEditStates.DeleteState,
        ChannelAddStates.DeleteState
    ]
)
async def not_delete(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()
    await call.message.delete()
    await review_channel(state=state, message=call.message, name_st=st)
