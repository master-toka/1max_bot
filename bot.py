#!/usr/bin/env python3
import asyncio
import logging
import os

try:
    from maxbot.bot import Bot
    from maxbot.dispatcher import Dispatcher
    from maxbot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Установите: pip install umaxbot")
    exit(1)

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "f9LHodD0cOK2Kds4gdFs3YnLHX14diXeMOThXWoPWt3H7KZm7UF0A3ZEtj6GK6q5K0bY2smJORcRiMLxDWM1")
DISCUSSION_GROUP_ID = os.getenv("DISCUSSION_GROUP_ID", "-72394786012668")
try:
    DISCUSSION_GROUP_ID = int(DISCUSSION_GROUP_ID)
except (ValueError, TypeError):
    DISCUSSION_GROUP_ID = None

BUTTON_TEXT = "💬 Перейти к обсуждению"
# ================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)  # <-- Dispatcher принимает bot


def create_discussion_button(group_id: int) -> InlineKeyboardMarkup:
    group_link = f"max://chat/{group_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_TEXT, url=group_link)]
    ])


@dp.message()  # <-- декоратор для обработки всех сообщений
async def handle_message(message: Message):
    chat_type = getattr(message.chat, 'type', None)
    
    # Если сообщение из канала
    if chat_type == "channel":
        if DISCUSSION_GROUP_ID is None:
            logger.error("❌ DISCUSSION_GROUP_ID не задан!")
            return
        
        post_text = message.text or ""
        logger.info(f"Новый пост в канале: {post_text[:50]}...")
        
        try:
            keyboard = create_discussion_button(DISCUSSION_GROUP_ID)
            await bot.update_message(
                chat_id=message.chat.id,
                message_id=message.id,
                text=post_text,
                reply_markup=keyboard
            )
            logger.info(f"✅ Кнопка добавлена")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
        return
    
    # Если сообщение в личку
    if message.text and message.text.startswith("/start"):
        await bot.send_message(
            chat_id=message.sender.id,
            text=f"🤖 Бот запущен!\n\nID этой группы: `{message.chat.id}`",
            format="markdown"
        )


async def main():
    logger.info("🚀 Запуск бота...")
    logger.info(f"✅ Токен: {BOT_TOKEN[:10]}...")
    logger.info(f"✅ Группа обсуждений: {DISCUSSION_GROUP_ID}")
    
    try:
        # ПРАВИЛЬНЫЙ ВЫЗОВ: start_polling у диспетчера
        await dp.start_polling()
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
