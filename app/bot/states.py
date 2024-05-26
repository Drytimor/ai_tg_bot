from aiogram.fsm.state import StatesGroup, State


class ChoicesModels(StatesGroup):

    model_choices = State()


class Payments(StatesGroup):

    payment = State()

