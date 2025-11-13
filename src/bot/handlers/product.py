from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import  StateFilter

from ..states import AddProduct, SetProduct
from ...core.auth.admin import USED_ADMINS
from ...core.database import ProductManager
from ...core.config import config
from ...errors import ProductNotFindError


class ProductAPI:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.api = ProductManager(session)
        self.router = Router()
        self._register_handlers()
    
    def _register_handlers(self):
        self.router.message(Command("addprod"))(self.start_add_product)
        self.router.message(AddProduct.waiting_for_title, F.text)(self.process_name)
        self.router.message(AddProduct.waiting_for_description, F.text)(self.process_description)
        self.router.message(AddProduct.waiting_for_price, F.text)(self.process_price)
        self.router.message(AddProduct.waiting_for_count, F.text)(self.process_count)
        self.router.message(AddProduct.waiting_for_poster, F.photo)(self.process_photo)
        self.router.message(Command("cancel"), StateFilter(AddProduct, SetProduct))(self.cancel_add_product)
        self.router.message(Command("getprod"))(self.get_product)
        self.router.message(Command("delprod"))(self.del_product)
        self.router.message(Command("setprod"))(self.set_product)
        self.router.message(SetProduct.waiting_for_command, F.text)(self.set_command)
    
    async def start_add_product(self, message: Message, state: FSMContext):
        if message.from_user.id not in USED_ADMINS:
            await message.answer("Вы не авторизованы как админ")
            return 
        await message.answer(
            "Давайте добавим новый товар!\nВведите название товара:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(AddProduct.waiting_for_title)
    
    async def process_name(self, message: Message, state: FSMContext):
        await state.update_data(title=message.text)
        await message.answer("Отлично! Теперь введите описание товара:")
        await state.set_state(AddProduct.waiting_for_description)
        
    async def process_description(self, message: Message, state: FSMContext):
        await state.update_data(description=message.text)
        await message.answer("Теперь введите цену товара (только числа):")
        await state.set_state(AddProduct.waiting_for_price)
        
    async def process_price(self, message: Message, state: FSMContext):
        try:
            price = float(message.text)
            await state.update_data(price=price)
            await message.answer("Введите количество товара:")
            await state.set_state(AddProduct.waiting_for_count)
        except ValueError:
            await message.answer("Пожалуйста, введите корректную цену (число):")
            
    async def process_count(self, message: Message, state: FSMContext):
        try:
            count = int(message.text)
            await state.update_data(count=count)
            await message.answer("Теперь отправьте фото товара:")
            await state.set_state(AddProduct.waiting_for_poster)
        except ValueError:
            await message.answer("Пожалуйста, введите корректное количество (целое число):")
            
    async def process_photo(self, message: Message, state: FSMContext):
        photo = message.photo[-1]
        photo_id = photo.file_id
        
        data = await state.get_data()
        file = await message.bot.get_file(photo_id)
        download_path = config.PATH_TO_SAVE_IMAGE / (photo_id + Path(file.file_path).suffix if file.file_path else ".jpg")
        await message.bot.download_file(file.file_path, download_path)
        
        await self.api.create_product(**data, poster=str(download_path))
        
        await message.answer_photo(
            photo_id,
            caption=f"✅ Товар успешно добавлен!\n\n"
                f"📦 Название: {data['title']}\n"
                f"📝 Описание: {data['description']}\n"
                f"💰 Цена: {data['price']} руб.\n"
                f"📊 Количество: {data['count']} шт."
        )
        
        await state.clear()
    
    async def cancel_add_product(message: Message, state: FSMContext):
        await message.answer("Добавление товара отменено.")
        await state.clear()

    async def get_product(self, msg: Message):
        try:
            _, id = [x.strip() for x in msg.text.split()]
            product = await self.api.get_product(id)
            if not product:
                await msg.answer(
                    f"Продукт под id {id} не был найден"
                )
                return
            data = product.as_dict()
            try:
                await msg.answer_photo(
                    FSInputFile(data['poster']),
                    caption=(
                        f"Название: {data['title']}\n"
                        f"Описание: {data['description']}\n"
                        f"Цена: {data['price']}\n"
                        f"Количество на складе: {data['count']}"
                    )
                )
            except Exception as e:
                await msg.answer_photo(
                    FSInputFile(config.img_404),
                    caption=(
                        f"Название: {data['title']}\n"
                        f"Описание: {data['description']}\n"
                        f"Цена: {data['price']}\n"
                        f"Количество на складе: {data['count']}\n\n"
                        f"DEBUG: {str(e)}"
                    )
                )
        except ValueError:
            await msg.answer("Неправильный вид данных\nпожалуйста введите данные в виде <code>/getprod [ID продукта]</code>", parse_mode="HTML")
            
    async def del_product(self, msg: Message):
        if msg.from_user.id not in USED_ADMINS:
            await msg.answer("Вы не авторизованы как админ")
            return 
        try:
            _, id = [x.strip() for x in msg.text.split()]
            try:
                await self.api.delete_product(int(id))
                await msg.answer(
                    f"Продукт под id {id} был успешно удалён"
                )
            except ProductNotFindError:
                await msg.answer(
                    f"Продукт под id {id} не был найден"
                )
            except TypeError:
                await msg.answer(
                    f"Перданная строка не является ID"
                )
            
        except ValueError:
            await msg.answer("Неправильный вид данных\nпожалуйста введите данные в виде <code>/delprod [ID продукта]</code>", parse_mode="HTML")
                
    async def set_product(self, msg: Message, state: FSMContext):
        if msg.from_user.id not in USED_ADMINS:
            await msg.answer("Вы не авторизованы как админ")
            return 
        try:
            _, id = [x.strip() for x in msg.text.split()]
            product = await self.api.get_product(int(id))
            if not product:
                await msg.answer(
                    f"Продукт под id {id} не был найден"
                )
                return 
        except TypeError:
            await msg.answer(
                f"Перданная строка не является ID"
            )
            return
        except ValueError:
            await msg.answer("Неправильный вид данных\nпожалуйста введите данные в виде <code>/setprod [ID продукта]</code>", parse_mode="HTML")
            return
        
        data = product.as_dict()
        try:
            await msg.answer_photo(
                FSInputFile(data['poster']),
                caption=(
                    "Что изменить в продукте?\n"
                    f"Название: {data['title']}\n"
                    f"Описание: {data['description']}\n"
                    f"Цена: {data['price']}\n"
                    f"Количество на складе: {data['count']}\n\n"
                    "Писать в виде [КЛЮЧ]: [ЗНАЧЕНИЕ]"
                )
            )
        except Exception as e:
            await msg.answer_photo(
                FSInputFile(config.img_404),
                caption=(
                    "Что изменить в продукте?\n"
                    f"Название: {data['title']}\n"
                    f"Описание: {data['description']}\n"
                    f"Цена: {data['price']}\n"
                    f"Количество на складе: {data['count']}\n\n"
                    "Писать в виде [КЛЮЧ]: [ЗНАЧЕНИЕ]\n"
                    f"DEBUG: {str(e)}"
                )
            )
        finally:
            await state.update_data(id=id)
            await state.set_state(SetProduct.waiting_for_command)
            

    
    async def set_command(self, msg: Message, state: FSMContext):
        states = {
            'Название': 'title',
            'Постер': 'poster',
            'Цена': 'price',
            'Количество на складе': 'count',
            'Описание': 'description'
        }
        try:
            data = await state.get_data()
            key, value = msg.text.split(": ", 1)
            await self.api.custom_product(data['id'], states[key.strip()], value.strip())
            await state.clear()
            await msg.answer("Успешно удалось изменить продукт!")
            
        except ValueError:
            await msg.answer("Писать в виде [КЛЮЧ]: [ЗНАЧЕНИЕ]")
            
        except KeyError:
            await msg.answer(f"Не существующий ключ {key} пожалуйста используйте данные ключи: {list(states.keys())}")
            
        except Exception as e:
            await msg.answer(f"Неизвестная ошибка во время изменении продукта: {e}")
    
        
def init(session: AsyncSession) -> list[Router]:
    return [
        ProductAPI(session).router
    ]