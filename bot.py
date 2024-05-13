import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup
from config import ELMA_TOKEN, ELMA_URL_ZADACHI, ELMA_URL_APP, TOKEN
from logger import init_logger

logger = logging.getLogger('main.bot.py')
bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class ElmaBot(StatesGroup):
    getting_task_name_from_user = State()
    getting_task_description_from_user = State()
    confirming_task_description_from_user = State()
    choosing_task_responsible = State()
    getting_deadline_from_user = State()
    choosing_task_napravlenie = State()
    confirming_task_creating = State()
    creating_task_in_elma = State()


@dp.message(StateFilter(None), Command("start"))
async def start(message: types.Message, state: FSMContext):
    """Reply to a start message and create a button to start creating a task."""
    logger.debug(f'Пользователь - {message.from_user.id} начал работу с ботом')
    from utils.variables import create_start_buttons
    keyboard = await create_start_buttons()
    await message.answer(f"Привет, {message.from_user.first_name}! Я твой помощник для работы в ELMA!",
                         reply_markup=keyboard)
    await state.set_state(ElmaBot.getting_task_name_from_user)


@dp.message(ElmaBot.getting_task_name_from_user)
async def get_task_name_from_user(message: types.Message, state: FSMContext):
    """If the user clicked to create a task, then send him a message to get the task name."""
    logger.debug(f'-----START---get_task_name_from_user------')
    logger.critical(f'message | {message.text}')
    if message.text == "Создать задачу":
        await message.answer('Введите название задачи')
        await state.set_state(ElmaBot.getting_task_description_from_user)
    else:
        await state.clear()
        await message.answer('Действие отменено')
        return
    logger.debug(f'-----FINISH---get_task_name_from_user------')


@dp.message(ElmaBot.getting_task_description_from_user)
async def get_task_description_from_user(message: types.Message, state: FSMContext):
    """Write the task name to state and ask user to add description"""
    logger.debug(f'-----START---get_task_description_from_user------')
    logger.critical(f'message | {message.text}')
    __name = message.text
    await state.update_data(__name=__name)
    await message.answer(f"Название задачи: {__name}")
    await message.answer("Добавьте описание к задаче. Если описание не требуется, напишите Нет")
    await state.set_state(ElmaBot.confirming_task_description_from_user)
    logger.debug(f'-----FINISH---get_task_description_from_user------')


@dp.message(ElmaBot.confirming_task_description_from_user)
async def confirm_task_description_from_user(message: types.Message, state: FSMContext):
    """Write the description to state and ask user to choose responsible"""
    logger.debug(f'-----START---confirm_task_description_from_user------')
    logger.critical(f'message | {message.text}')
    if message.text == 'Нет':
        await state.update_data(opisanie=" ")
        await message.answer("Хорошо, описание не будет добавлено.")
    else:
        await state.update_data(opisanie=message.text)
        await message.answer("Описание добавлено.")
    markup = await choose_responsible_markup()
    await message.answer('Выберите ответственного!', reply_markup=markup)
    await state.set_state(ElmaBot.choosing_task_responsible)
    logger.debug(f'-----FINISH---confirm_task_description_from_user------')


async def choose_responsible_markup():
    """Create buttons attached to the message (InlineKeyboardButton) to select responsible.
    Get the list of users by API request to ELMA.
    """
    # logger.debug(f'-----START---executors_markup------')
    from utils.variables import create_inline_buttons_user_list
    builder = await create_inline_buttons_user_list()
    # logger.debug(f'-----FINISH---executors_markup------')
    return builder.as_markup()


@dp.callback_query(ElmaBot.choosing_task_responsible)
async def callback_query_responsible(call, state: FSMContext):
    """Hide the buttons, get the selected executor and write it to state, then ask user to add deadline"""
    logger.debug(f'-----START---callback_query_responsible------')
    new_markup = InlineKeyboardMarkup(inline_keyboard=[])
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        reply_markup=new_markup)
    logger.debug(call.data)
    await state.update_data(otvetstvennyi=[call.data])
    await bot.send_message(call.message.chat.id, "Определите дедлайн задачи в формате ГГГГ-ММ-ДД")
    await state.set_state(ElmaBot.getting_deadline_from_user)
    logger.debug(f'-----FINISH---callback_query_responsible------')


@dp.message(ElmaBot.getting_deadline_from_user)
async def get_deadline_from_user(message: types.Message, state: FSMContext):
    """Write the deadline to state and get the direction of the work from user."""
    logger.debug(f'-----START---get_deadline_from_user------')
    logger.critical(f'message | {message.text}')
    await message.answer(f"Срок выполнения задачи: {message.text}")
    from utils.variables import create_deadline
    deadline = await create_deadline(message)
    await state.update_data(dedlain=deadline)
    markup = await choose_napravlenie_markup()
    await message.answer('Выберите направление!', reply_markup=markup)
    await state.set_state(ElmaBot.choosing_task_napravlenie)
    logger.debug(f'-----FINISH---get_deadline_from_user------')


async def choose_napravlenie_markup():
    """Create buttons attached to the message (InlineKeyboardButton) to select the direction.
    """
    # logger.debug(f'-----START---napravlenie_markup------')
    from utils.variables import create_inline_buttons_napravlenie
    builder = await create_inline_buttons_napravlenie()
    # logger.debug(f'-----FINISH---napravlenie_markup------')
    return builder.as_markup()


@dp.callback_query(ElmaBot.choosing_task_napravlenie)
async def callback_query_napravlenie(call, state: FSMContext):
    """Hide the buttons, get the selected direction and write it to state. If the user has chosen the Marketplace
    direction, then ask him to add marketing specialist. Then ask to confirm task"""
    logger.debug(f'-----START---callback_query_responsible------')
    new_markup = InlineKeyboardMarkup(inline_keyboard=[])
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        reply_markup=new_markup)
    await state.update_data(napravlenie=[{"code": call.data}])
    if call.data == "marketpleis":
        keyboard = await create_buttons_marketolog()
        await bot.send_message(call.message.chat.id, "Вы выбрали направление Маркетплейс. Хотите добавить участие "
                                                     "маркетолога в задаче?", reply_markup=keyboard)
        await state.set_state(ElmaBot.confirming_task_creating)
    else:
        from utils.variables import confirm_task
        keyboard = await confirm_task()
        await bot.send_message(call.message.chat.id, "Подтвердите создание задачи", reply_markup=keyboard)
        await state.set_state(ElmaBot.creating_task_in_elma)
    logger.debug(f'-----FINISH---callback_query_responsible------')


async def create_buttons_marketolog():
    """Create buttons attached to the message (InlineKeyboardButton) to add marketing specialist.
    """
    # logger.debug(f'-----START---napravlenie_markup------')
    from utils.variables import create_buttons_marketolog
    builder = await create_buttons_marketolog()
    # logger.debug(f'-----FINISH---napravlenie_markup------')
    return builder.as_markup()


@dp.callback_query(ElmaBot.confirming_task_creating)
async def callback_query_confirm_task(call, state: FSMContext):
    """Hide the buttons, and write marketing specialist to state"""
    logger.debug(f'-----START---callback_query_confirm_task------')
    new_markup = InlineKeyboardMarkup(inline_keyboard=[])
    await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        reply_markup=new_markup)
    if call.data == "yes":
        await state.update_data(marketolog=["cc354f70-2090-4147-9eb1-386b78be5ea0"])
        await bot.send_message(call.message.chat.id, "Маркетолог добавлен!")
    else:
        await state.update_data(marketolog=[])
        await bot.send_message(call.message.chat.id, "Хорошо. Маркетолог не будет добавлен!")
    from utils.variables import confirm_task
    keyboard = await confirm_task()
    await bot.send_message(call.message.chat.id, "Подтвердите создание задачи", reply_markup=keyboard)
    await state.set_state(ElmaBot.creating_task_in_elma)
    logger.debug(f'-----FINISH---callback_query_confirm_task------')


@dp.message(ElmaBot.creating_task_in_elma, F.text == "Подтверждаю")
async def create_task_in_elma(message: types.Message, state: FSMContext):
    """Create task in ELMA by API request. If creation was successful, send message with link to the task"""
    logger.debug(f'-----START---create_task_in_elma------')
    logger.critical(f'message | {message.text}')
    user_state_data = await state.get_data()
    data = {"context": {"__name": user_state_data['__name']}}
    data["context"]["opisanie"] = user_state_data['opisanie']
    data["context"]["otvetstvennyi"] = user_state_data['otvetstvennyi']
    data["context"]["dedlain"] = user_state_data['dedlain']
    data["context"]["napravlenie"] = user_state_data['napravlenie']
    data["context"]["marketolog"] = user_state_data['marketolog']
    logger.critical(data)
    response = requests.post(ELMA_URL_APP + '/create', json=data,
                             headers={'Authorization': 'Bearer ' + ELMA_TOKEN})
    if response.status_code != 200:
        logger.debug('Ошибка подключения к ELMA.')
        await message.answer("Ошибка создания задачи")
        return
    result = response.json()
    logger.critical(f'{result}')
    if not result['success']:
        logger.debug('Ошибка создания задачи в ELMA.')
        await message.answer('Что-то пошло не так')
    else:
        logger.debug('Задача создана успешно.')
        await message.answer(
            'Задача создана успешно [Посмотреть задачу](' + ELMA_URL_ZADACHI + '(p:item/ot/zadachi/' +
            result['item']['__id'] + '\))', parse_mode='MarkdownV2')
        logger.critical(f'{result["success"]}')
    logger.debug(f'-----FINISH---create_task_in_elma------')


@dp.message(ElmaBot.creating_task_in_elma, F.text == "Отменить")
async def cancel_creating_task(message: types.Message, state: FSMContext):
    """Stop creating a task"""
    logger.debug(f'-----START---cancel_creating_task------')
    await state.clear()
    await message.answer("Создание задачи отменено!")
    logger.debug(f'-----FINISH---cancel_creating_task------')
    return


def register_bot_steps(dp: Dispatcher):
    dp.message.register(start, state=None)
    dp.message.register(get_task_name_from_user, state=ElmaBot.getting_task_name_from_user)
    dp.message.register(get_task_description_from_user, state=ElmaBot.getting_task_description_from_user)
    dp.message.register(confirm_task_description_from_user, state=ElmaBot.confirming_task_description_from_user)
    dp.callback_query.register(callback_query_responsible, state=ElmaBot.choosing_task_responsible)
    dp.message.register(get_deadline_from_user, state=ElmaBot.getting_deadline_from_user)
    dp.callback_query.register(callback_query_napravlenie, state=ElmaBot.choosing_task_napravlenie)
    dp.callback_query.register(callback_query_confirm_task, state=ElmaBot.confirming_task_creating)
    dp.message.register(create_task_in_elma, state=ElmaBot.creating_task_in_elma)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    init_logger('main')
    asyncio.run(main())
