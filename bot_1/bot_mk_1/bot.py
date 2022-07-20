import asyncio
import sentry_sdk

from aiogram import executor

from utils import on_startup_notify, on_shutdown
from loader import SSL_CERTIFICATE, ssl_context
from handlers import dp
from data.config import WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from utils.set_bot_commands import set_default_commands
from utils.pars.video_parser import VideoParser
from utils.misc.logs.logs_db_orm.management_logs import autocommit_logs, autodelete_logs

sentry_sdk.init(
    "https://71f736a392564121a460b13e54ec51c6@o1267040.ingest.sentry.io/6453112",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


async def on_startup(dispatcher):
    loop = asyncio.get_running_loop()
    channel = VideoParser(dp)

    await dp.bot.delete_webhook()

    await dp.bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=SSL_CERTIFICATE
    )

    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)

    loop.create_task(channel.search_new_video())
    loop.create_task(autocommit_logs())
    loop.create_task(autodelete_logs())


if __name__ == '__main__':
    # dev
    # executor.start_polling(
    #     dispatcher=dp,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     skip_updates=True,
    # )

    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        ssl_context=ssl_context
    )

