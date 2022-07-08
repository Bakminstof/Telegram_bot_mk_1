import ssl

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.config import WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, BOT_TOKEN


# BOT
bot: Bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(bot, storage=storage)
DEBUG: bool = True

# SSL
# ssl_context = None
# SSL_CERTIFICATE = None
#
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

with open(WEBHOOK_SSL_CERT, "rb") as serf:
    CERT = serf.read()

SSL_CERTIFICATE = CERT

ssl_context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
