#!/usr/bin/env python3
"""
Бот для MAX мессенджера: автоматическое добавление кнопки "Обсудить"
под каждым постом в канале.
"""

import asyncio
import logging
import os
from typing import Optional

try:
    from maxbot.bot import Bot
    from maxbot.dispatcher import Dispatcher
    from maxbot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
except ImportError as e:
    print(f"Ошибка импорта umaxbot: {e}")
    print("Установите: pip install umaxbot")
    exit(1)

# ========== НАСТРОЙКИ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCUSSION_GROUP_ID = os.getenv("DISCUSSION_GROUP_ID")
if DISCUSSION_GROUP_ID:
    try:
        DISCUSSION_GROUP_ID = int(DISCUSSION_GROUP_ID)
    except ValueError:
        DISCUSSION_GROUP_ID = None

BUTTON_TEXT = os.getenv("BUTTON_TEXT", "💬 Перейти к обсуждению")
# =======================================================

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Проверка наличия токена
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не задан! Укажите его в переменной окружения.")
    exit(1)

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)  # <-- Важно: Dispatcher принимает bot


def create_discussion_button(group_id: int) -> InlineKeyboardMarkup:
    """Создать inline-кнопку для перехода в группу обсуждений."""
    group_link = f"max://chat/{group_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXT, url=group_link)]
    ])


async def process_channel_post(message: Message):
    """Обработка нового поста в канале."""
    if DISCUSSION_GROUP_ID is None:
        logger.error("❌ DISCUSSION_GROUP_ID не задан!")
        return
    
    post_text = message.text or ""
    logger.info(f"Новый пост в канале {message.chat.id}: {post_text[:50]}...")
    
    try:
        keyboard = create_discussion_button(DISCUSSION_GROUP_ID)
        await bot.update_message(
            chat_id=message.chat.id,
            message_id=message.id,
            text=post_text,
            reply_markup=keyboard
        )
        logger.info(f"✅ Кнопка добавлена под постом {message.id}")
    except Exception as e:
        logger.error(f"❌ Ошибка при добавлении кнопки: {e}")


@dp.message()  # <-- Декоратор для обработки сообщений
async def handle_message(message: Message):
    """Обработчик всех сообщений."""
    # Проверяем тип чата
    chat_type = getattr(message.chat, 'type', None)
    
    # Если сообщение из канала — обрабатываем как пост
    if chat_type == "channel":
        await process_channel_post(message)
        return
    
    # Если сообщение из личного чата
    if message.text:
        if message.text.startswith("/start"):
            help_text = (
                f"🤖 **Бот для комментариев в каналах MAX**\n\n"
                f"📌 **ID этого чата:** `{message.chat.id}`\n\n"
                f"🔧 **Текущие настройки:**\n"
                f"- Группа обсуждений: `{DISCUSSION_GROUP_ID or 'не задана'}`\n\n"
                f"📖 **Инструкция:**\n"
                f"1. Добавьте бота в канал (сначала подписчик, потом админ)\n"
                f"2. Добавьте бота в группу обсуждений (админом)\n"
                f"3. Напишите любое сообщение в группе — я покажу её ID\n"
                f"4. Установите DISCUSSION_GROUP_ID через переменную окружения\n"
                f"5. Перезапустите бота"
            )
            await bot.send_message(
                chat_id=message.sender.id,
                text=help_text,
                format="markdown"
            )
        else:
            await bot.send_message(
                chat_id=message.sender.id,
                text="👋 Привет! Отправь /start для справки."
            )


async def main():
    """Основная функция запуска."""
    logger.info("🚀 Запуск бота...")
    logger.info(f"✅ Токен: {BOT_TOKEN[:10]}...")
    
    if DISCUSSION_GROUP_ID:
        logger.info(f"✅ Группа обсуждений: {DISCUSSION_GROUP_ID}")
    else:
        logger.warning("⚠️ DISCUSSION_GROUP_ID не задан")
    
    try:
        # Для библиотеки umaxbot метод polling — это асинхронная функция,
        # которая запускается на объекте Dispatcher
        await dp.start_polling()  # <-- Правильный вызов
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())
