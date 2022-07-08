import asyncio
import datetime

from sqlalchemy import delete

from utils.misc.logs.logs_db_orm.logs_schema import a_session_log, BaseLoggerTable

LOG_CACHE = []


# autocommit logs
async def autocommit_logs():
    lock = asyncio.Lock()

    while True:
        await asyncio.sleep(10)

        async with lock:
            a_session_log.add_all(LOG_CACHE)

            LOG_CACHE.clear()

        await a_session_log.commit()


# delete old logs
async def autodelete_logs():
    last_day: datetime.datetime | None = None

    while True:
        current_day = datetime.datetime.now()

        if last_day and (last_day.date() != current_day.date()):
            delta = current_day - datetime.timedelta(days=1)

            del_stmt = delete(BaseLoggerTable).filter(BaseLoggerTable.dtime <= delta)

            await a_session_log.execute(del_stmt)

        last_day = current_day

        await asyncio.sleep(3600 * 4)
