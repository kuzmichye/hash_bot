import re
import hashlib
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# === Константы из .env ===
PHONE_SALT = os.getenv("PHONE_SALT", "default_salt")
BOT_TOKEN = os.getenv("BOT_TOKEN")

def normalize_phone(phone: str) -> str:
    if not phone:
        raise ValueError("Номер телефона не может быть пустым")
    phone = re.sub(r'\s+', '', phone.strip())
    if not phone.startswith('+'):
        raise ValueError("Номер телефона должен начинаться с +")
    if not re.match(r'^\+\d+$', phone):
        raise ValueError("Номер телефона должен содержать только цифры после +")
    return phone

def hash_phone(phone: str) -> str:
    normalized_phone = normalize_phone(phone)
    return hashlib.sha512((normalized_phone + PHONE_SALT).encode()).hexdigest()

# === aiogram 3 ===
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# приветствие
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("👋 Привет! Введите номер телефона в формате +XXXXXXXXXX")

# эхо/хэш
@dp.message(F.text)
async def echo_or_hash(message: Message):
    text = message.text.strip()
    if text.startswith("+") and re.match(r'^\+\d+$', text):
        try:
            hashed = hash_phone(text)
            await message.answer(f"🔑 Хэш номера:\n{hashed}")
        except ValueError as e:
            await message.answer(f"Ошибка: {e}")
    else:
        await message.answer(f"Эхо: {text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
