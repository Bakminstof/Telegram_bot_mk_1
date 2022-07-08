from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.movie_list.callback_data_watch_list import callback_watch_list

watch_list_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Редактировать',
                callback_data=callback_watch_list.new(
                    change='yes'
                )
            ),
        ]
    ]
)


watch_add_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Добавить запись',
                callback_data=callback_watch_list.new(
                    change='add'
                )
            ),
        ]
    ]
)
