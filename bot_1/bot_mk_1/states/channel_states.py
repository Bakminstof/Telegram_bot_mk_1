from aiogram.dispatcher.filters.state import StatesGroup, State


class ChannelAddStates(StatesGroup):
    ChangeState = State()

    EditState = State()

    EditNameState = State()
    EditNameState2 = State()
    EditUrlState = State()

    DeleteState = State()


class ChannelEditStates(StatesGroup):
    ChangeState = State()

    EditState = State()

    EditNameState = State()
    EditUrlState = State()

    DeleteState = State()

