#!/usr/bin/env python3
"""
Бот для MAX мессенджера: автоматическое добавление кнопки "Обсудить"
под каждым постом в канале.
"""

import asyncio
import logging
import os
from typing import Optional

# Пробуем импортировать umaxbot
try:
    from maxbot.bot import Bot
    from maxbot.dispatcher import Dispatcher
    from maxbot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
except ImportError as e:
    print(f"Ошибка импорта umaxbot: {e}")
    print("Убедитесь, что библиотека установлена: pip install umaxbot")
    exit(1)

# ========== НАСТРОЙКИ ==========
# Токен бота, полученный от @MasterBot
BOT_TOKEN = os.getenv("BOT_TOKEN", "f9LHodD0cOK2Kds4gdFs3YnLHX14diXeMOThXWoPWt3H7KZm7UF0A3ZEtj6GK6q5K0bY2smJORcRiMLxDWM1")

# ID группы, куда будут дублироваться посты для обсуждений
# Получить можно, написав боту в группе любое сообщение — ID выведется в консоль
DISCUSSION_GROUP_ID = os.getenv("DISCUSSION_GROUP_ID", None)
if DISCUSSION_GROUP_ID:
    try:
        DISCUSSION_GROUP_ID = int(DISCUSSION_GROUP_ID)
    except ValueError:
        DISCUSSION_GROUP_ID = None

# Текст на кнопке
BUTTON_TEXT = "💬 Перейти к обсуждению"

# Сообщение, добавляемое к посту в группе обсуждений
DISCUSSION_HEADER = "📢 **Обсуждение поста:**\n\n"
# ================================

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)


def create_discussion_button(group_id: int) -> InlineKeyboardMarkup:
    """Создать inline-кнопку для перехода в группу обсуждений."""
    group_link = f"max://chat/{group_id}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXT, url=group_link)]
    ])


async def process_channel_post(message: Message):
    """
    Обработка нового поста в канале.
    Добавляет кнопку под постом.
    """
    if DISCUSSION_GROUP_ID is None:
        logger.error("DISCUSSION_GROUP_ID не задан! Бот не может добавить кнопку.")
        return
    
    # Получаем текст поста
    post_text = message.text or ""
    
    logger.info(f"Новый пост в канале {message.chat.id}: {post_text[:50]}...")
    
    # Добавляем кнопку под оригинальным постом
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


@dp.message()
async def handle_message(message: Message):
    """
    Обработчик всех сообщений.
    """
    # Проверяем, является ли чат каналом
    chat_type = getattr(message.chat, 'type', None)
    
    # Если сообщение из канала — обрабатываем как пост
    if chat_type == "channel":
        await process_channel_post(message)
        return
    
    # Если сообщение из личного чата или группы
    if message.text:
        if message.text.startswith("/start"):
            help_text = (
                f"🤖 **Бот для комментариев в каналах MAX**\n\n"
                f"📌 **ID этого чата:** `{message.chat.id}`\n\n"
                f"🔧 **Настройка:**\n"
                f"1. Добавьте бота в канал (сначала в подписчики, потом админом)\n"
                f"2. Добавьте бота в группу обсуждений (админом)\n"
                f"3. Напишите любое сообщение в группе — я покажу её ID\n"
                f"4. Установите переменную окружения DISCUSSION_GROUP_ID\n\n"
                f"📖 После настройки бот будет автоматически добавлять кнопку 'Обсудить' под каждым постом."
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
    else:
        # Если сообщение без текста (например, фото)
        logger.info(f"Получено сообщение без текста из чата {message.chat.id}")


async def main():
    """Основная функция запуска бота."""
    logger.info("🚀 Запуск бота...")
    
    # Проверяем токен
    if BOT_TOKEN == "ваш_токен_бота":
        logger.error("❌ Не задан BOT_TOKEN! Укажите токен в переменной окружения или в коде.")
        return
    
    # Проверяем настройки
    if DISCUSSION_GROUP_ID is None:
        logger.warning(
            "⚠️ DISCUSSION_GROUP_ID не задан. "
            "Бот будет работать, но кнопка не будет добавляться. "
            "Укажите ID группы обсуждений в переменной окружения."
        )
    else:
        logger.info(f"✅ Группа обсуждений: ID={DISCUSSION_GROUP_ID}")
    
    logger.info(f"✅ Бот запущен, токен: {BOT_TOKEN[:10]}...")
    
    # Запускаем polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())
