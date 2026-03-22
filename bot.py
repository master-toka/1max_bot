#!/usr/bin/env python3
import asyncio
import logging
import os

from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "ваш_токен")
DISCUSSION_GROUP_ID = int(os.getenv("DISCUSSION_GROUP_ID", "-72394786012668"))

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message_created()
async def on_message(event: MessageCreated):
    msg = event.message
    
    # Проверяем, что сообщение из канала
    if msg.chat.type == "channel":
        post_text = msg.body.text if msg.body else ""
        logger.info(f"Новый пост в канале: {post_text[:50]}...")
        
        # Создаём inline-клавиатуру с кнопкой
        keyboard = {
            "inline_keyboard": [[{
                "text": "💬 Перейти к обсуждению",
                "url": f"max://chat/{DISCUSSION_GROUP_ID}"
            }]]
        }
        
        try:
            await bot.update_message(
                chat_id=msg.chat.id,
                message_id=msg.id,
                text=post_text,
                reply_markup=keyboard
            )
            logger.info("✅ Кнопка добавлена")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")


async def main():
    logger.info("🚀 Запуск бота...")
    await dp.start_polling(bot)  # <-- для maxapi: передаём bot в start_polling


if __name__ == "__main__":
    asyncio.run(main())
