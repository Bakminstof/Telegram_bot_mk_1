from sqlalchemy import Column
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.dialects.mysql import INTEGER, SMALLINT, VARCHAR, DATETIME

from data.config import LOGS_DB

Base = declarative_base()

engine_log = create_async_engine('sqlite+aiosqlite:///{db}'.format(db=LOGS_DB))

async_session = sessionmaker(
    bind=engine_log,
    expire_on_commit=False,
    class_=AsyncSession
)

a_session_log = async_session()


# tables
class BaseLoggerTable(Base):
    __tablename__ = 'base_logger'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    level = Column(VARCHAR(8), nullable=False)
    name = Column(VARCHAR(20), nullable=False)
    dtime = Column(DATETIME, nullable=False)
    line = Column(SMALLINT(unsigned=True), nullable=False)
    message = Column(VARCHAR, nullable=False)
    exec_text = Column(VARCHAR, default=None)

    def __repr__(self) -> str:
        return '(id: {id}, ' \
               'level: {level}, ' \
               'name: {name}, ' \
               'dtime: {dtime}, ' \
               'line: {line}, ' \
               'message: {message}, ' \
               'exec_text: {exec_text})'.format(
            id=self.id,
            level=self.level,
            name=self.name,
            dtime=self.dtime,
            line=self.line,
            message=self.message,
            exex_text=self.exec_text
        )
