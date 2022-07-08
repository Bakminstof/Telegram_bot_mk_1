import logging.config
import re
import urllib3

from data.config import video_pattern
from utils.misc.logs.logger import dict_config


logging.config.dictConfig(dict_config)
pars_logger = logging.getLogger('pars')


class ChannelParser:
    def __init__(self, url: str):
        self.last_video: str | None = None
        self.location = url
        self.timeout = 5
        self.exist = False
        self.exception = False
        self.logger_base_msg = '{name} id=\'{id_}\' Try №{try_}'

    def get_data(self):
        pars_logger.debug('Start check channel')

        for try_ in range(1, 3):
            try:
                pars_logger.debug(self.logger_base_msg.format(name="get_data", id_=None, try_=try_))

                http = urllib3.PoolManager()
                resp = http.request('GET', url=self.location + '/videos', timeout=self.timeout)
                text = resp.data.decode('utf-8')

                if resp.status != 200:
                    self.exception = True
                    pars_logger.warning(f' HTTP code {resp.status}')
                else:
                    self.exist = True

                videos = re.findall(video_pattern, text)

                if videos:
                    self.last_video = videos[0]

                http.clear()
                break

            except Exception as ex:
                pars_logger.warning(
                    f'{self.logger_base_msg.format(name="get_data", id_=None, try_=try_)} => exception:'
                    f'\n\ttype -> "{type(ex)}",'
                    f'\n\ttext -> ({ex})'
                )
                continue
        else:
            try_ = 'last try'
            pars_logger.critical(
                f'{self.logger_base_msg.format(name="get_data", id_=None, try_=try_)} => critical'
                f'\nCant get html page:'
                f'\n\turl="{self.location}"'
            )

    def check_except(self) -> bool:
        if self.exception:
            return True
        else:
            return False

    def check_exist(self) -> bool:
        if self.exist:
            return True
        else:
            return False
