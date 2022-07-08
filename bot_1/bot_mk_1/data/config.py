from environs import Env

yes = '\u2705'  # ✅
no = '\u2b55\ufe0f'  # ⭕
format_movie_name_pattern = "<b> ~ {n}</b>  <i>'{t}'</i>  {c}"
format_channel_name_pattern = '<i><b> ~ {n}</b></i>'
video_pattern = r'/watch\?v=[^"\']*'

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")

ADMINS = env.list('ADMINS')

LOGS_DB = env.str('LOGS_DB')
MAIN_DB = env.str('MAIN_DB')

IP = env.str('IP')

# webhook settings
WEBHOOK_HOST = f'https://{IP}'
WEBHOOK_PORT = env.str('WEBHOOK_PORT')
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'

WEBHOOK_URL = f'{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}'

WEBHOOK_SSL_CERT = env.str('WEBHOOK_SSL_CERT')
WEBHOOK_SSL_PRIV = env.str('WEBHOOK_SSL_PRIV')

# webserver settings
WEBAPP_HOST = env.str("WEBAPP_HOST")
WEBAPP_PORT = env.str("WEBAPP_PORT")
