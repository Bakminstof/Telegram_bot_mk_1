import logging.config

from aiogram import types
from sqlalchemy import select
from collections import OrderedDict
from aiogram.dispatcher import FSMContext

from loader import dp
from data.config import format_channel_name_pattern
from utils.misc.logs.logger import dict_config
from states.channel_states import ChannelEditStates, ChannelAddStates
from main_db.main_db_orm.mian_db_schema import a_session_main, SubscriptionsTable
from keyboards.inline.movie_list.ik_movies_list import watch_add_keyboard, watch_list_keyboard

logging.config.dictConfig(dict_config)
subscription_channels_logger = logging.getLogger('subscription_channels')


# get user subscriptions
async def get_subscriptions_list(message: types.Message):
    subscription_channels_logger.info('Completing subscriptions list')
    stmt = select(
        SubscriptionsTable.id,
        SubscriptionsTable.custom_name,
        SubscriptionsTable.location,
        SubscriptionsTable.last_video
    ).filter(SubscriptionsTable.user_id.is_(message.from_user.id))

    res = await a_session_main.execute(stmt)

    subscriptions_list = res.all()

    if subscriptions_list:
        channels = OrderedDict(
            {
                i + 1:
                    {
                        'id_in_db': channel[0],
                        'custom_name': channel[1],
                        'location': channel[2],
                        'format_name': format_channel_name_pattern.format(n=channel[1]),
                        'last_video': channel[3]
                    }
                for i, channel in enumerate(subscriptions_list)
            }
        )

        return channels

    else:
        return OrderedDict()


@dp.message_handler(commands=['channels'], state=None)
async def all_channels(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        subscriptions = data.get('subscriptions')

    if subscriptions:
        subscription_channels_logger.info('Using cache')
        msg = '<i>Мои подписки</i>:\n' + '\n'.join(map(lambda x: x.get('format_name'), subscriptions.values()))

        await message.answer(msg, reply_markup=watch_list_keyboard)
        await ChannelEditStates.ChangeState.set()

    else:
        subscription_channels_logger.info('Using DB')
        subs = await get_subscriptions_list(message)

        async with state.proxy() as data:
            data['subscriptions'] = subs

        if subs:
            msg = '<i>Мои подписки</i>:\n' + '\n'.join(map(lambda x: x.get('format_name'), subs.values()))

            await ChannelEditStates.ChangeState.set()
            await message.answer(msg, reply_markup=watch_list_keyboard)

        else:
            await ChannelAddStates.ChangeState.set()
            await message.answer('Ваш список пуст', reply_markup=watch_add_keyboard)
