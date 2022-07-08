import sys

from utils.misc.logs.logger.loggers_handlers import ConsoleHandler, LogsDBHandler


dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "%(levelname)s | %(name)s | %(asctime)s | %(lineno)s | %(message)s",
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    "handlers": {
        "console": {
            "()": ConsoleHandler,
            "level": "DEBUG",
            'stream': sys.stdout
        },
        "logs_db_handler": {
            "()": LogsDBHandler,
            "level": "DEBUG",
            "formatter": "base",
        }
    },
    "loggers": {
        "notify": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "init_main_db": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "init_logs_db": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "start": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "aiosqlite": {
            "level": "DEBUG",
            "handlers": [
                # "console",
            ],
            'propagate': False
        },
        "subscription_channels": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "watch": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "subscription_write_in_db": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "delete_subs": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "subscription_review": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "movie_write_in_db": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "delete_mov": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "review_movie": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "channel": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "ChannelDebugLogger": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },
        "pars": {
            "level": "DEBUG",
            "handlers": [
                "console",
                'logs_db_handler'
            ],
            'propagate': False
        },

    },
    'root': {
        "level": "DEBUG",
        "handlers": [
            'console',
            'logs_db_handler'
        ],
    }
}
