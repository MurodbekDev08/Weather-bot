import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8526016141:AAHUxrRAqSJvSuCKlZ7oTRqtQO83uOEyOag"
OPENAI_API_KEY = "sk-abc123xyz456EXAMPLE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Tugmalar uchun shaharlar ---
cities = ["Tashkent", "Samarkand", "Bukhara", "Namangan", "Fergana"]
city_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=city, callback_data=city)]
        for city in cities
    ]
)

# --- ChatGPT bilan ishlash funksiyasi ---
async def explain_weather_with_chatgpt(city, weather_desc, temp, feels):
    prompt = (
        f"Sizga ob-havo ma'lumotlari berildi:\n"
        f"Shahar: {city}\n"
        f"Harorat: {temp}°C, Sezilishi: {feels}°C\n"
        f"Holati: {weather_desc}\n\n"
        f"Foydalanuvchiga sodda va tushunarli tarzda tushuntiring."
    )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=json_data) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                return "ChatGPT bilan bog‘liq muammo yuz berdi."

# --- Fake ob-havo ma'lumotlari ---
def generate_fake_weather():
    temp = random.randint(-5, 40)
    feels = temp + random.randint(-2, 3)
    desc = random.choice([
        "Quyoshli", "Bulutli", "Yomg‘irli", "Qorli", "Shamolli", "Bo‘ronli"
    ])
    return temp, feels, desc

# --- /start komandasi ---
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🌦 Assalomu alaykum! Shaharni tanlang yoki nomini yozing:",
        reply_markup=city_keyboard
    )

# --- Inline tugma bosilganda ---
@dp.callback_query()
async def city_callback(query):
    city = query.data
    await query.message.answer(f"⏳ {city} bo‘yicha ob-havo olinmoqda...")
    await send_weather(query.message, city)
    await query.answer()

# --- Ob-havo yuborish funksiyasi ---
async def send_weather(message: Message, city: str):
    temp, feels, desc = generate_fake_weather()

    # ChatGPT izohini olish
    explanation = await explain_weather_with_chatgpt(city, desc, temp, feels)

    await message.answer(
        f"🌆 *{city}* ob-havosi:\n"
        f"🌡 Harorat: {temp}°C\n"
        f"🤔 Seziladi: {feels}°C\n"
        f"📝 Holat: {desc}\n\n"
        f"💬 *Izoh ChatGPT tomonidan:*\n{explanation}",
        parse_mode="Markdown"
    )

# --- Shahar nomi matn orqali yuborilganda ---
@dp.message(F.text)
async def custom_city(message: Message):
    city = message.text.strip()
    await send_weather(message, city)

# --- Bot ishga tushishi ---
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
