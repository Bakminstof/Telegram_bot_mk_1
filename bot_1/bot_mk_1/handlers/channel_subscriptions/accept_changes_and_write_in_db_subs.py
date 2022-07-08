import logging.config


from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp
from utils.misc.logs.logger import dict_config
from states.channel_states import ChannelEditStates, ChannelAddStates
from handlers.base_handers.channels_h import get_subscriptions_list
from main_db.main_db_orm.mian_db_schema import SubscriptionsTable, a_session_main
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_accept

logging.config.dictConfig(dict_config)
subscription_write_in_db_logger = logging.getLogger('subscription_write_in_db')


# write all changes into db `handler
@dp.callback_query_handler(
    callback_accept.filter(act='save_all'),
    state=[
        ChannelEditStates.EditState,
        ChannelAddStates.EditState
    ]
)
async def write_all_changes_into_db(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        to_update = data.get('update', {}).values()
        to_save = data.get('save', {}).values()

        data.pop('channel_add')
        data.pop('channel_edit')
        data.pop('update')
        data.pop('save')

    if to_save:
        save = [
            SubscriptionsTable(
                custom_name=channel.get('custom_name'),
                location=channel.get('location'),
                last_video=channel.get('last_video'),
                user_id=call.from_user.id
            ) for channel in to_save
        ]

        subscription_write_in_db_logger.info(
            'Saved: {}'.format(
                ', '.join(
                    [
                        sub.get('custom_name')
                        for sub in to_save
                    ]
                )
            )
        )

        a_session_main.add_all(save)

        await a_session_main.commit()

    if to_update:
        update = [
            {
                'id': sub.get('id'),
                'custom_name': sub.get('custom_name'),
                'location': sub.get('location'),
                'last_video': sub.get('last_video'),
                'user_id': call.from_user.id
            } for sub in to_update
        ]

        subscription_write_in_db_logger.info(
            'Updated: {}'.format(
                ', '.join(
                    [
                        sub.get('custom_name')
                        for sub in update
                    ]
                )
            )
        )

        await a_session_main.run_sync(lambda session: session.bulk_update_mappings(SubscriptionsTable, update))
        await a_session_main.commit()

    subscription_write_in_db_logger.warning('Accept changes')

    await call.message.edit_text('Сохранено!')

    subscriptions = await get_subscriptions_list(message=call.message)

    async with state.proxy() as data:
        data['subscriptions'] = subscriptions

    await state.reset_state(with_data=False)
