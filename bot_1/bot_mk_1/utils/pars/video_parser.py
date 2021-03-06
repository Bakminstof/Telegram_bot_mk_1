import multiprocessing
import random
import re
import asyncio
import logging.config
import time
import urllib3

from typing import Dict, List, Any
from aiogram import Dispatcher
from threading import Thread
from sqlalchemy import select
from multiprocessing import Process, Manager

from data.config import video_pattern
from utils.misc.logs.logger import dict_config
from main_db.main_db_orm.mian_db_schema import SubscriptionsTable, a_session_main, UsersTable
from utils.misc.logs.logger.base_debug_logger_decorator import logger_decorator

logging.config.dictConfig(dict_config)
channel_logger = logging.getLogger('channel')


# searching new videos
class VideoParser:
    def __init__(self, dp: Dispatcher) -> None:
        self.stmt = select(
            SubscriptionsTable.id,
            SubscriptionsTable.location,
            SubscriptionsTable.last_video,
            SubscriptionsTable.custom_name,
            SubscriptionsTable.user_id,
        )
        self.dp = dp
        self.timeout = 10
        self.channels = {}
        self.updates = {}

    # get channels data
    @logger_decorator(channel_logger)
    async def __get_channels_data(self) -> None:
        result = await a_session_main.execute(self.stmt)
        channel_data = result.all()

        for channel in channel_data:
            self.channels[channel[0]] = {
                'channel_id': channel[0],
                'location': channel[1],
                'last_video': channel[2],
                'custom_name': channel[3],
                'user_id': channel[4],
            }

        channel_logger.debug(f'Channels data: {self.channels}')

    # get channel's HTML page. Thread work
    def __get_html_page(self, barrier: multiprocessing.Barrier) -> None:
        channel_logger.debug('Load HTML pages')

        threads = [
            HTMLThread(
                url=channel.get('location') + '/videos',
                timeout=self.timeout,
                id_channel=id_,
                channels=self.channels,
                barrier=barrier
            ) for id_, channel in self.channels.items()
        ]

        workers = []

        for th in threads:
            th.start()
            workers.append(th)

        for worker in workers:
            worker.join(self.timeout)

            del worker

        channel_logger.debug('Save HTML pages')

    # refactor channels. Process work
    def __refactor_channels(self) -> None:
        channel_logger.debug('Start refactoring')

        channels_keys = list(self.channels.keys())
        parts_keys = []

        manager = Manager()
        updates_manager = manager.dict()

        if len(channels_keys) <= 30:
            parts_keys.append(channels_keys)
        else:
            while len(channels_keys) > 30:
                part = channels_keys[:30]
                channels_keys = channels_keys[30:]
                parts_keys.append(part)

        for part in parts_keys:
            for id_channel in part:
                processes = [
                    ChanelRefactorProcess(
                        id_channel=id_channel,
                        channels=self.channels,
                        updates=updates_manager,
                        args=(updates_manager,)
                    )
                ]
                workers = []

                for proc in processes:
                    proc.start()
                    workers.append(proc)

                for worker in workers:
                    worker.join(self.timeout)

                    del worker

        self.updates.update(updates_manager)

        del updates_manager
        channel_logger.debug('End refactoring')

    # searching new videos
    @logger_decorator(channel_logger)
    async def search_new_video(self) -> None:
        while True:
            channel_logger.debug('Start checking')

            await self.__get_channels_data()
            barrier = multiprocessing.Barrier(len(self.channels.keys()))

            if self.channels:
                self.__get_html_page(barrier=barrier)
                self.__refactor_channels()

                if self.updates:
                    await self.__update_db()
                    await self.__send_new_videos()

                # clear cache
                self.channels.clear()
                self.updates.clear()

            time_ = random.randint(1200, 1800)  # sec
            channel_logger.info(f'Go sleep {time_} sec.')
            await asyncio.sleep(time_)  # sleep

    # update db
    @logger_decorator(channel_logger)
    async def __update_db(self) -> None:
        channel_logger.debug('Update db')

        to_update = [
            {
                'id': id_,
                'last_video': channel.get('last_video')
            } for id_, channel in self.updates.items()
        ]

        await a_session_main.run_sync(lambda session: session.bulk_update_mappings(SubscriptionsTable, to_update))
        await a_session_main.commit()

        channel_logger.debug(
            'Done update: {}'.format(
                [
                    c.get('custom_name')
                    for c in self.updates.values()
                ]
            )
        )

    # send new videos to users
    @logger_decorator(channel_logger)
    async def __send_new_videos(self) -> None:
        youtube_url = 'https://www.youtube.com'
        msg = '<b><i>~ {ch} ~\n???????????????? ?????????? ??????????!\n\n{v}</i></b>'

        stmt = select(UsersTable.telegram_id, UsersTable.notifications)
        res = await a_session_main.execute(stmt)

        notifications = res.all()
        notif = {n[0]: n[1] for n in notifications}

        channel_logger.debug('Completing send list')

        to_send = [
            self.dp.bot.send_message(
                chat_id=channel.get('user_id'),
                text=msg.format(
                    ch=channel.get('custom_name'),
                    v='\n\n'.join(
                        [
                            f'<a href="{youtube_url + video_part}">????????????????</a>'
                            for video_part in channel.get('new_videos')
                        ]
                    )
                )
            )
            for channel in self.updates.values()
            if notif.get(channel.get('user_id')) and channel.get('new_videos', False)
        ]

        await asyncio.gather(*to_send)

        channel_logger.debug('Send new videos')


class HTMLThread(Thread):
    def __init__(
            self,
            url: str,
            timeout: int,
            barrier: multiprocessing.Barrier,
            id_channel: int,
            channels: Dict[int, Dict[str, Any]]
    ):
        super().__init__()
        self.timeout = timeout
        self.url = url
        self.id_ = id_channel if id_channel else self.native_id
        self.logger_base_msg = '{name} id=\'{id_}\' Try ???{try_}, url: {url}'
        self.channels = channels
        self.http_status_code = None
        self.barrier = barrier

    def run(self) -> None:
        for try_ in range(1, 5):
            try:
                channel_logger.debug(self.logger_base_msg.format(name=self.name, id_=self.id_, try_=try_, url=self.url))

                http = urllib3.PoolManager()
                resp = http.request('GET', url=self.url, timeout=self.timeout)
                text = resp.data.decode('utf-8')

                self.http_status_code = resp.status

                channel_logger.debug(
                    '{} => success'.format(
                        self.logger_base_msg.format(
                            name=self.name,
                            id_=self.id_,
                            try_=try_,
                            url=self.url
                        )
                    )
                )

                self.channels[self.id_]['html_page'] = text

                http.clear()
                del http

                self.barrier.wait()

                break

            except Exception as ex:
                del http

                random_time = random.randint(5, 15)
                channel_logger.warning(
                    f'{self.logger_base_msg.format(name=self.name, id_=self.id_, try_=try_, url=self.url)} => exception:'
                    f'\n\ttype -> "{type(ex)}",'
                    f'\n\ttext -> ({ex})'
                    f'\n\tgo sleep {random_time} sec. and try again')

                time.sleep(random_time)
                continue
        else:
            try_ = 'last try'
            channel_logger.error(
                f'{self.logger_base_msg.format(name=self.name, id_=self.id_, try_=try_, url=self.url)} => error'
                f'\nCant get html page:'
                f'\n\turl="{self.url}"'
            )

            self.channels[self.id_]['html_page'] = None
            self.barrier.wait()


class ChanelRefactorProcess(Process):
    def __init__(
            self,
            id_channel: int,
            channels: Dict[int, Dict[str, Any]],
            updates: Dict[int, Dict[str, Any]],
            args=()
    ):
        super().__init__(args=args)
        # global
        self.updates: dict = updates
        # current
        self.id_channel: int = id_channel
        self.current_channel: dict = channels.get(id_channel)
        self.url: str = channels.get(self.id_channel).get('location')
        self.html_page: str = channels.get(self.id_channel).get('html_page')
        self.last_video: str = channels.get(self.id_channel).get('last_video')
        self.custom_name: str = channels.get(self.id_channel).get('custom_name')
        self.all_videos = []

    def run(self) -> None:
        channel_logger.debug(f'Start proc id: {self.pid}')
        html = self.html_page

        if html:
            self.all_videos = self.__scrap_videos(html_page=html, url=self.url)
            self.__comparison_func()
        else:
            channel_logger.error(f'Proc \'{self.pid}\', url {self.url} HTML page is None')

    @staticmethod
    def __scrap_videos(html_page: str, url: str) -> List[str | None]:
        channel_logger.debug('Start scrapping')
        video_urls = re.findall(video_pattern, html_page)

        if video_urls:
            channel_logger.debug(f'Find videos: {video_urls}')
        else:
            channel_logger.warning(f'Don\'t find videos on channel: url="{url}"')

        return video_urls

    def __comparison_func(self) -> None:
        new_videos = []

        for video in self.all_videos:
            if self.last_video not in self.all_videos:
                self.current_channel['last_video'] = self.all_videos[0]
                self.updates[self.id_channel] = self.current_channel
                break

            elif video != self.last_video:
                new_videos.append(video)

            else:
                break

        if new_videos:
            channel_logger.debug(
                'Channel: \'{name}\''
                '\ndetect new videos: [{v}]'.format(
                    name=self.custom_name,
                    v=', '.join(new_videos)
                )
            )

            self.current_channel['new_videos'] = new_videos
            self.current_channel['last_video'] = new_videos[0]
            self.updates[self.id_channel] = self.current_channel
