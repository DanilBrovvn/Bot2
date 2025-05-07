import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import Command
import asyncio
import logging

# Загрузка переменных окружения из .env
load_dotenv(dotenv_path=r"F:D:\Program Files (x86)\.env")
API_TOKEN = os.getenv('API_TOKEN')
ADMIN_IDS = os.getenv('ADMIN_IDS')
ADMIN_IDS = [int(x) for x in ADMIN_IDS.split(',')] if ADMIN_IDS else []

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Главное меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="О курсе"),
            KeyboardButton(text="Программа курса"),
        ],
        [
            KeyboardButton(text="Частые вопросы"),
            KeyboardButton(text="✅ Записаться"),
        ]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот курса «Говорить не страшно». Чем могу помочь?", reply_markup=menu)

@dp.message(F.text == "О курсе")
async def about_course(message: types.Message):
    await message.answer_photo(
        photo="https://i.postimg.cc/T33tRJ1d/2.png",
        caption="Даты курса"
    )

@dp.message(F.text == "Программа курса")
async def course_program(message: types.Message):
    await message.answer_photo(
        photo="https://i.postimg.cc/dtBWPxqN/3.png",
        caption="Информация о курсе"
    )

@dp.message(F.text == "Частые вопросы")
async def faq(message: types.Message):
    await message.answer_photo(
        photo="https://i.postimg.cc/7YDBRkyT/1.png",
        caption="Частые вопросы"
    )

# Состояние для записи
user_data = {}

@dp.message(F.text == "✅ Записаться")
async def register_user(message: types.Message):
    await message.answer("Введите ваше имя и фамилию:")
    user_data[message.from_user.id] = {"step": "name"}

@dp.message(lambda m: m.from_user.id in user_data)
async def process_registration(message: types.Message):
    uid = message.from_user.id
    step = user_data[uid]["step"]

    if step == "name":
        user_data[uid]["name"] = message.text
        user_data[uid]["step"] = "phone"
        await message.answer("Введите ваш номер телефона (в формате +7...):")
    elif step == "phone":
        user_data[uid]["phone"] = message.text
        name = user_data[uid]["name"]
        phone = user_data[uid]["phone"]

        # Уведомление админу
        for admin_id in ADMIN_IDS:
            await bot.send_message(
                admin_id,
                f"📢 Новая заявка на курс:\n\nИмя: {name}\nТелефон: {phone}\nОт @{message.from_user.username}"
            )
        await message.answer("Спасибо! Мы с вами свяжемся 💬", reply_markup=menu)
        del user_data[uid]

@dp.message()
async def unknown_message(message: types.Message):
    await message.answer("Пожалуйста, выберите вариант из меню.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
