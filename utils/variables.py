from datetime import datetime, timezone
from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import requests
from aiogram.utils.keyboard import InlineKeyboardBuilder

import logger
from config import ELMA_TOKEN, ELMA_URL, ELMA_URL_ZADACHI, ELMA_URL_APP, TOKEN


async def create_deadline(message: types.Message):
    deadline_to_str = message.text + 'T12:00:00'
    sdelat_do = datetime.strptime(deadline_to_str, "%Y-%m-%dT%H:%M:%S").astimezone().isoformat()
    return sdelat_do


async def create_start_buttons():
    keyboard_create_task = [
        [KeyboardButton(text="Создать задачу")],
        # [KeyboardButton(text="Изменить статус задачи")],
        [KeyboardButton(text="Отмена")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_create_task,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Хотите создать задачу?"
    )
    return keyboard


async def create_inline_buttons_user_list():
    response = requests.get(ELMA_URL + '/pub/v1/user/list', headers={'Authorization': 'Bearer ' + ELMA_TOKEN})
    if response.status_code != 200:
        # logger.critical('Не удалось получить список сотрудников из ELMA.')
        return
    result = response.json()
    user_list = result['result']['result']
    # logger.critical(f'Список сотрудников - {user_list}')
    builder = InlineKeyboardBuilder()
    builder.row_width = len(user_list)
    for user in user_list:
        builder.add(
            InlineKeyboardButton(text=user['__name'], callback_data=user['__id'])
        )
    builder.adjust(1)
    return builder


async def create_inline_buttons_napravlenie():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Маркетплейс", callback_data="marketpleis"),
        InlineKeyboardButton(text="B2B", callback_data="b2b"),
        InlineKeyboardButton(text="Аналитик", callback_data="analitik"),
    )
    builder.adjust(1)
    return builder


async def confirm_task():
    keyboard_confirm_task = [
        [KeyboardButton(text="Подтверждаю")],
        [KeyboardButton(text="Отменить")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_confirm_task,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Подтвердите создание задачи"
    )
    return keyboard


async def create_buttons_marketolog():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Да", callback_data="yes"),
        InlineKeyboardButton(text="Нет", callback_data="no"),
    )
    return builder
