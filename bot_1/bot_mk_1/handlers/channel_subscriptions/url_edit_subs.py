import re

from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext

from loader import dp
from states.channel_states import ChannelEditStates, ChannelAddStates
from utils.pars.channel_parser import ChannelParser
from handlers.channel_subscriptions.review_subs import review_channel
from keyboards.inline.movie_edit.callback_data_watch_edit import callback_watch_edit


# start edit URL channel `handler
@dp.callback_query_handler(
    callback_watch_edit.filter(edit='link'),
    state=[
        ChannelEditStates.EditState,
        ChannelAddStates.EditState,
    ]
)
async def edit_url(call: CallbackQuery, state: FSMContext):
    st = await state.get_state()

    if st == ChannelAddStates.EditState.state:
        await ChannelAddStates.EditUrlState.set()

    else:
        await ChannelEditStates.EditUrlState.set()

    await call.message.edit_text('Вставьте ссылку на канал', reply_markup=None)


# edit channel URL `handler
@dp.message_handler(state=[ChannelAddStates.EditUrlState, ChannelEditStates.EditUrlState])
async def edit_url_subscription(message: Message, state: FSMContext):
    st = await state.get_state()

    if st == ChannelAddStates.EditUrlState.state:
        subscription = 'channel_add'
    else:
        subscription = 'channel_edit'

    res = re.search(r'http.*', message.text)

    if res:
        channel_url = res.group()
        channel_check = False

        async with state.proxy() as data:
            for i, ch in data.get('subscriptions').items():
                if ch.get('location') == channel_url:
                    channel_check = True
                    ch['id'] = i
                    break

        if channel_check:
            await message.answer('Канал уже есть в списке')

            async with state.proxy() as data:
                data['channel_edit'] = ch

            await ChannelEditStates.EditState.set()
            st = await state.get_state()
            await review_channel(message=message, state=state, name_st=st)

        else:
            ch_parser = ChannelParser(channel_url)
            ch_parser.get_data()

            if ch_parser.check_except():
                await message.answer('Упс :/\n Попробуйте ещё раз')

            elif ch_parser.check_exist():
                async with state.proxy() as data:
                    data[subscription]['last_video'] = ch_parser.last_video
                    data[subscription]['location'] = ch_parser.location

                await message.answer('Добавлено')

                st = await state.get_state()
                await review_channel(message=message, state=state, name_st=st)

            else:
                await message.answer('Такого канала не существует')

            del ch_parser
    else:
        await message.answer('Некорректная ссылка')
