from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from ...core.auth.admin import ADMINS
from ...core.auth.admin import USED_ADMINS

router = Router()

@router.message(Command("login"))
async def cmd_login(message: Message):
    if message.from_user.id in USED_ADMINS:
        await message.answer("Вы уже админ!")
        return
    
    try:
        _, login, password = [x.strip() for x in message.text.split()]
    except ValueError:
        await message.answer("Неправильные введённые данные\nПишите в виде: <code>/login [ЛОГИН] [ПАРОЛЬ]</code>", parse_mode="HTML")
        return
    
    if login not in ADMINS:
        await message.answer(f"Пользователя {login} не существует")
        return
    
    elif str(ADMINS[login]) != password:
        await message.answer(f"Пароль не верный")
        return
    
    USED_ADMINS.add(message.from_user.id)
    await message.answer(f"Успешная авторизация!")
    
