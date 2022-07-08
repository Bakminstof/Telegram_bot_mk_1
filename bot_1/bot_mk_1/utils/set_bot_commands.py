from aiogram import types, Dispatcher

from utils.misc.logs.logger import logger_decorator


@logger_decorator()
async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("watch", "Список просмотра"),
            types.BotCommand("channels", "Список подписок"),
            types.BotCommand("cancel", "Отменить все действия"),
            types.BotCommand("help", "Список команд")
        ]
    )
