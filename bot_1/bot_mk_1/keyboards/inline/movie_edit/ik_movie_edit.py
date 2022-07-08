from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.config import no, yes
from keyboards.inline.movie_edit.callback_data_watch_edit import (
    callback_watch_edit,
    callback_type_edit,
    callback_accept
)
from keyboards.inline.movie_list.callback_data_watch_list import callback_watch_list

movie_edit_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Название',
                callback_data=callback_watch_edit.new(
                    edit='name',
                )
            ),
            InlineKeyboardButton(
                text='Тип',
                callback_data=callback_watch_edit.new(
                    edit='type',
                )
            ),
            InlineKeyboardButton(
                text='Статус',
                callback_data=callback_watch_edit.new(
                    edit='status',
                )
            )
        ],
        [
            InlineKeyboardButton(
                text='Удалить',
                callback_data=callback_watch_edit.new(
                    edit='del',
                )
            )
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=callback_watch_edit.new(
                    edit='back',
                )
            )
        ]
    ]
)

type_edit_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="'Ф' - фильм",
                callback_data=callback_type_edit.new(
                    type='F'
                )
            ),
            InlineKeyboardButton(
                text="'С' - сериал",
                callback_data=callback_type_edit.new(
                    type='S'
                )
            ),
            InlineKeyboardButton(
                text="'А' - аниме",
                callback_data=callback_type_edit.new(
                    type='A'
                )
            )
        ]
    ]
)

accept_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Да",
                callback_data=callback_accept.new(
                    act='yes'
                )
            ),
            InlineKeyboardButton(
                text="Нет",
                callback_data=callback_accept.new(
                    act='no'
                )
            )
        ]
    ]
)

watched_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Просмотрено {}".format(yes),
                callback_data=callback_accept.new(
                    act='yes'
                )
            ),
            InlineKeyboardButton(
                text="Ещё нет {}".format(no),
                callback_data=callback_accept.new(
                    act='no'
                )
            )
        ]
    ]
)
edit_movies_list_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Добавить запись',
                callback_data=callback_watch_list.new(
                    change='add'
                )
            ),
        ],
        [
            InlineKeyboardButton(
                text="Сохранить все изменения",
                callback_data=callback_accept.new(
                    act='save_all'
                )
            )
        ]

    ]
)

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=callback_watch_edit.new(
                    edit='back',
                )
            )
        ]
    ]
)

sub_edit_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Название',
                callback_data=callback_watch_edit.new(
                    edit='name',
                )
            ),
            InlineKeyboardButton(
                text='Ссылка',
                callback_data=callback_watch_edit.new(
                    edit='link',
                )
            )
        ],
        [
            InlineKeyboardButton(
                text='Удалить',
                callback_data=callback_watch_edit.new(
                    edit='del',
                )
            )
        ],
        [
            InlineKeyboardButton(
                text='Назад',
                callback_data=callback_watch_edit.new(
                    edit='back',
                )
            )
        ]
    ]
)
