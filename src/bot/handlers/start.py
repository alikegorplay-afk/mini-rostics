from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        (
            "Привет! Я админ панель для сайта <b>MiniRostics</b>\n"
            "Моя цель простое управление сайта без всяких ваших <b>BITRIX</b>\n"
            "Сразу скажу, админы уже определены\n"
            "Поэтому если ты чужак, пожалуйста покинь чат\n"
            "А если тебе далин логин и пароль, пропиши данную команду\n"
            "<code>/login [ЛОГИН] [ПАРОЛЬ]</code>"
        ),
        parse_mode="HTML"
    )

@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        (
            "Команды:\n"
            "1. /login - Авторизация в систему\n"
            "2. /help - Получение данной информации\n"
            "\nРабота с продуктами\n"
            "1. /addprod - Добавить продукт в БД <b>ТРЕБУЮТ ПРАВА АДМИНА</b>\n"
            "2. /delprod - Удалить продукт из БД <b>ТРЕБУЮТ ПРАВА АДМИНА</b>\n"
            "3. /setprod - Изменить уже существующий продукт\n <b>ТРЕБУЮТ ПРАВА АДМИНА</b>\n"
            "4. /getprod - получить продукт\n"
            "\nРабота с заказами\n"
            "1. /getord - получить подробную ифнормацию об заказе [В разработке]"
        ),
        parse_mode="HTML"
    )