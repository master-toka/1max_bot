import asyncio
import logging
from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated
from maxapi.exceptions import APIException

logging.basicConfig(level=logging.INFO)

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "f9LHodD0cOK2Kds4gdFs3YnLHX14diXeMOThXWoPWt3H7KZm7UF0A3ZEtj6GK6q5K0bY2smJORcRiMLxDWM1"
YOUR_CHANNEL_ID = -71133736408572  # ID канала, за которым следим. Например, -1001234567890
DISCUSSION_CHAT_NAME = "Комментарии"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Глобальная переменная для хранения ID чата обсуждений. В реальном боте лучше сохранять в БД.
discussion_chat_id = -72394786012668

async def get_or_create_discussion_chat():
    """Проверяет, создан ли чат обсуждений, и создает его при необходимости."""
    global discussion_chat_id
    if discussion_chat_id:
        return discussion_chat_id

    # 1. Пытаемся найти существующий чат по названию (это упрощенный поиск).
    # В реальном приложении вам нужно сохранять ID чата после его создания.
    # Например, в файле или базе данных.
    # Для простоты примера мы будем создавать чат заново, если он не был создан в этой сессии.
    logging.info("Чат обсуждений не найден. Создаем новый...")

    # 2. Создаем новый групповой чат.
    # Внимание: API бота MAX пока не имеет прямого метода для создания группы.
    # Это ограничение платформы. Бот может быть добавлен в существующую группу.
    # Обходной путь: создать группу вручную (через интерфейс MAX) и добавить туда бота.
    # Затем указать ID этой группы в коде.
    # Поэтому в этом примере мы будем использовать предварительно созданную группу.
    
    # Вместо создания, мы ожидаем, что вы вручную создадите группу, добавите туда бота
    # и укажете её ID здесь.
    # Это основное ограничение текущего Bot API MAX.
    raise NotImplementedError(
        "Бот не может создать группу самостоятельно. "
        "Пожалуйста, создайте группу вручную, добавьте в нее бота и укажите её ID в переменной DISCUSSION_CHAT_ID."
    )

@dp.message_created()
async def handle_new_post(event: MessageCreated):
    """Обработчик всех новых сообщений."""
    global discussion_chat_id
    
    # Проверяем, что сообщение пришло из нашего канала.
    if event.message.chat.id != YOUR_CHANNEL_ID:
        return

    # Игнорируем служебные сообщения и сообщения без текста (например, только фото).
    if not event.message.body or not event.message.body.text:
        return

    # 1. Получаем или создаем чат для обсуждений.
    try:
        chat_id_for_discussion = await get_or_create_discussion_chat()
    except NotImplementedError as e:
        logging.error(e)
        # В реальном боте здесь можно отправить сообщение создателю канала.
        return

    # 2. Копируем пост в чат обсуждений.
    post_text = event.message.body.text
    # Добавляем ссылку на оригинальный пост для контекста (опционально).
    # Ссылку на сообщение в MAX можно сформировать, но это сложно.
    # Просто скопируем текст.
    await bot.send_message(
        chat_id=chat_id_for_discussion,
        text=f"**Обсуждение поста из канала:**\n\n{post_text}"
    )
    logging.info(f"Пост скопирован в чат {chat_id_for_discussion}")

    # 3. (Опционально) Отредактировать исходный пост, добавив кнопку-ссылку на чат обсуждений.
    # Это сложная часть, так как требует сохранения message_id и последующего вызова edit_message.
    # Для простоты опустим в этом примере.

async def main():
    # Удаляем webhook, если он был установлен, чтобы использовать polling.
    await bot.delete_webhook()
    # Запускаем получение обновлений.
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
