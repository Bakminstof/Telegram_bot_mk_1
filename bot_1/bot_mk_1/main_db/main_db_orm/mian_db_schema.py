import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, DATETIME, BOOLEAN, CHAR

from data.config import MAIN_DB

Base = declarative_base()

engine_main = create_async_engine('sqlite+aiosqlite:///{db}'.format(db=MAIN_DB))

async_session = sessionmaker(
    bind=engine_main,
    expire_on_commit=False,
    class_=AsyncSession
)

a_session_main = async_session()


# tables
# users table
class UsersTable(Base):
    __tablename__ = 'users'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    telegram_id = Column(INTEGER(unsigned=True), nullable=False, unique=True)
    first_name = Column(VARCHAR(50), nullable=False)
    last_name = Column(VARCHAR(50))
    notifications = Column(BOOLEAN, default=True)
    date_first_auth = Column(DATETIME, default=datetime.datetime.now())

    rls_watch = relationship(
        'WatchTable',
        backref=backref(
            'users',
            cascade="all, delete-orphan",
            single_parent=True
        ),
    )

    subscriptions = relationship(
        'SubscriptionsTable',
        backref=backref(
            'users',
            cascade='all, delete-orphan',
            single_parent=True
        )
    )

    def __repr__(self) -> str:
        return 'id: {id}, ' \
               'telegram_id: {telegram_id}, ' \
               'first_name: {first_name}, ' \
               'last_name: {last_name}, ' \
               'date_first_auth: {date_first_auth}'.format(
            id=self.id,
            telegram_id=self.telegram_id,
            first_name=self.first_name,
            last_name=self.last_name,
            date_first_auth=self.date_first_auth,
        )


# channel subscriptions table
class SubscriptionsTable(Base):
    __tablename__ = 'subscriptions'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    custom_name = Column(VARCHAR(50), nullable=False)
    location = Column(VARCHAR(50), nullable=False)
    last_video = Column(VARCHAR(30))

    user_id = Column(INTEGER(unsigned=True), ForeignKey('users.telegram_id'), nullable=False)

    def __repr__(self) -> str:
        return 'id: {id}, ' \
               'custom_name: {custom_name}, ' \
               'location: {location}, ' \
               'last_video: {last_video},' \
               'user_id: {user_id}'.format(
            id=self.id,
            custom_name=self.custom_name,
            location=self.location,
            last_video=self.last_video,
            user_id=self.user_id
        )


# watch table
class WatchTable(Base):
    __tablename__ = 'watch'

    id = Column(INTEGER(unsigned=True), primary_key=True)
    name = Column(VARCHAR(50), nullable=False)
    type = Column(CHAR(1), nullable=False)
    watched = Column(BOOLEAN, default=False)
    user_id = Column(INTEGER(unsigned=True), ForeignKey('users.telegram_id'), nullable=False)

    def __repr__(self) -> str:
        return 'id: {id}, ' \
               'name: {name}, ' \
               'type: {type}, ' \
               'watched: {watched}, ' \
               'user_id: {user_id}'.format(
            id=self.id,
            name=self.name,
            type=self.type,
            watched=self.watched,
            user_id=self.user_id,
        )
