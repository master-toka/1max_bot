#!/usr/bin/env python3
"""
Бот для MAX мессенджера: автоматическое добавление кнопки "Обсудить"
под каждым постом в канале. Пост дублируется в чат обсуждений.
"""

import asyncio
import logging
import os
from typing import Optional

from maxbot.bot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# ========== НАСТРОЙКИ ==========
# Токен бота, полученный от @MasterBot
BOT_TOKEN = "f9LHodD0cOK2Kds4gdFs3YnLHX14diXeMOThXWoPWt3H7KZm7UF0A3ZEtj6GK6q5K0bY2smJORcRiMLxDWM1"

# ID канала, в котором нужно отслеживать посты
# (можно оставить None, бот определит автоматически при первом сообщении)
CHANNEL_ID: Optional[int] = None

# ID группы, куда будут дублироваться посты для обсуждений
DISCUSSION_GROUP_ID: Optional[int] = None

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


async def get_chat_id_by_username(username: str) -> Optional[int]:
    """
    Получить ID чата по username.
    В MAX это работает только если бот уже добавлен в чат.
    """
    try:
        # Пробуем отправить тестовое сообщение себе для получения инфо
        me = await bot.get_me()
        logger.info(f"Бот запущен: @{me.username}")
        return None
    except Exception as e:
        logger.error(f"Ошибка получения информации: {e}")
        return None


async def get_group_id_by_name(group_name: str) -> Optional[int]:
    """Получить ID группы по названию (упрощённо — через поиск в обновлениях)."""
    # В MAX нет прямого метода поиска чата по названию.
    # Рекомендуется вручную указать ID группы в настройках.
    logger.warning(
        "Автоматическое определение ID группы не реализовано. "
        "Укажите DISCUSSION_GROUP_ID в коде."
    )
    return None


def create_discussion_button(group_id: int) -> InlineKeyboardMarkup:
    """Создать inline-кнопку для перехода в группу обсуждений."""
    # Ссылка на группу в формате max://chat/{id}
    group_link = f"max://chat/{group_id}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXT, url=group_link)]
    ])


async def process_channel_post(message: Message):
    """
    Обработка нового поста в канале.
    Дублирует пост в группу обсуждений и добавляет кнопку под оригиналом.
    """
    global CHANNEL_ID, DISCUSSION_GROUP_ID
    
    # Определяем ID канала, если ещё не задан
    if CHANNEL_ID is None:
        CHANNEL_ID = message.chat.id
        logger.info(f"Канал обнаружен: ID={CHANNEL_ID}, название={message.chat.title}")
    
    # Проверяем, что группа обсуждений настроена
    if DISCUSSION_GROUP_ID is None:
        logger.error("DISCUSSION_GROUP_ID не задан! Бот не может добавить кнопку.")
        return
    
    # Получаем текст поста
    post_text = message.text or ""
    
    logger.info(f"Новый пост в канале: {post_text[:50]}...")
    
    # 1. Отправляем пост в группу обсуждений (с заголовком)
    discussion_message = DISCUSSION_HEADER + post_text
    try:
        await bot.send_message(
            chat_id=DISCUSSION_GROUP_ID,
            text=discussion_message,
            format="markdown"
        )
        logger.info(f"Пост продублирован в группу {DISCUSSION_GROUP_ID}")
    except Exception as e:
        logger.error(f"Ошибка при дублировании в группу: {e}")
    
    # 2. Добавляем кнопку под оригинальным постом
    try:
        keyboard = create_discussion_button(DISCUSSION_GROUP_ID)
        
        # Редактируем сообщение, добавляя кнопку
        # (или отправляем новое с кнопкой, если нужно)
        await bot.update_message(
            chat_id=message.chat.id,
            message_id=message.id,
            text=post_text,  # сохраняем оригинальный текст
            reply_markup=keyboard
        )
        logger.info(f"Кнопка добавлена под постом {message.id}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении кнопки: {e}")


@dp.message()
async def handle_message(message: Message):
    """
    Обработчик всех сообщений.
    Если сообщение пришло из канала — обрабатываем как пост.
    """
    # Проверяем, является ли чат каналом
    # У каналов тип chat.type = "channel"
    if hasattr(message.chat, 'type') and message.chat.type == "channel":
        await process_channel_post(message)
        return
    
    # Если сообщение из личного чата — выводим ID чатов для настройки
    if message.text and message.text.startswith("/start"):
        await bot.send_message(
            chat_id=message.sender.id,
            text=f"🤖 Бот запущен!\n\n"
                 f"📌 **ID этого чата:** `{message.chat.id}`\n\n"
                 f"🔧 Для настройки бота:\n"
                 f"1. Добавьте бота в канал и группу обсуждений\n"
                 f"2. Укажите ID канала и группы в переменных CHANNEL_ID и DISCUSSION_GROUP_ID\n"
                 f"3. Перезапустите бота\n\n"
                 f"📖 Подробнее: https://github.com/Werdset/maxbot",
            format="markdown"
        )
        return
    
    # Для других сообщений в личке — просто игнорируем или отвечаем
    await bot.send_message(
        chat_id=message.sender.id,
        text="👋 Привет! Я бот для добавления комментариев к постам в канале.\n"
             "Отправь /start для справки."
    )


async def main():
    """Основная функция запуска бота."""
    logger.info("Запуск бота...")
    
    # Проверяем токен
    if BOT_TOKEN == "ваш_токен_бота":
        logger.error("❌ Не задан BOT_TOKEN! Укажите токен в коде.")
        return
    
    # Проверяем настройки
    if DISCUSSION_GROUP_ID is None:
        logger.warning(
            "⚠️ DISCUSSION_GROUP_ID не задан. "
            "Бот будет работать, но кнопка не будет добавляться. "
            "Укажите ID группы обсуждений."
        )
    else:
        logger.info(f"Группа обсуждений: ID={DISCUSSION_GROUP_ID}")
    
    # Запускаем polling (получение обновлений)
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())
