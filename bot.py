import asyncio
import logging
from maxapi import Bot, Dispatcher, F
from maxapi.types import MessageCreated

logging.basicConfig(level=logging.INFO)

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"
YOUR_CHANNEL_ID = ID_ВАШЕГО_КАНАЛА  # Например, -1001234567890
DISCUSSION_CHAT_ID = ID_ЧАТА_ОБСУЖДЕНИЙ  # ID группы, куда будут копироваться посты

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message_created(F.message.body.text)
async def handle_new_post(event: MessageCreated):
    """Обработчик новых сообщений."""
    
    # Правильный способ получить ID чата — через event.message.chat_id
    chat_id = event.message.chat_id
    
    # Проверяем, что сообщение пришло из нашего канала
    if chat_id != YOUR_CHANNEL_ID:
        logging.info(f"Сообщение из другого чата: {chat_id}")
        return
    
    # Получаем текст поста
    post_text = event.message.body.text
    logging.info(f"Новый пост в канале: {post_text[:50]}...")
    
    # Копируем пост в чат обсуждений
    try:
        await bot.send_message(
            chat_id=DISCUSSION_CHAT_ID,
            text=f"**📝 Новый пост для обсуждения:**\n\n{post_text}\n\n---\n💬 Комментируйте здесь 👆"
        )
        logging.info(f"✅ Пост скопирован в чат {DISCUSSION_CHAT_ID}")
    except Exception as e:
        logging.error(f"❌ Ошибка при отправке сообщения: {e}")

async def main():
    """Запуск бота."""
    logging.info("🚀 Бот запускается...")
    
    # Удаляем webhook, если был установлен
    try:
        await bot.delete_webhook()
        logging.info("✅ Webhook удален")
    except Exception as e:
        logging.info(f"Webhook не был установлен или уже удален: {e}")
    
    # Запускаем long polling
    logging.info("👂 Начинаем прослушивание сообщений...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
