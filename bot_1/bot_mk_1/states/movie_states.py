from aiogram.dispatcher.filters.state import StatesGroup, State


class MovieEditStates(StatesGroup):
    ChangeState = State()

    EditState = State()

    NameEditState = State()
    TypeEditState = State()
    StatusEditState = State()

    DeleteState = State()


class MovieAddStates(StatesGroup):
    AddMovieState = State()

    EditState = State()

    NameEditState = State()
    TypeEditState = State()
    StatusEditState = State()

    DeleteState = State()
