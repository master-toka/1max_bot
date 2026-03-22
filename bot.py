from maxbot.bot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot("f9LHodD0cOK2Kds4gdFs3YnLHX14diXeMOThXWoPWt3H7KZm7UF0A3ZEtj6GK6q5K0bY2smJORcRiMLxDWM1")
dp = Dispatcher(bot)

@dp.message()
async def on_message(message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👋 Поздороваться", callback_data="hello")]
    ])
    await bot.send_message(
        chat_id=message.sender.id,
        text="Привет! Я бот для комментариев",
        reply_markup=keyboard
    )

@dp.callback()
async def on_callback(cb):
    if cb.payload == "hello":
        await bot.send_message(cb.user.id, "Приятно познакомиться!")

dp.start()
await bot.send_message(
    chat_id=channel_id,
    text=post_text,
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Перейти к обсуждению",
            url=f"max://chat/{discussion_group_id}"
        )]
    ])
)
