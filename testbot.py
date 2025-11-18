import io
import os
import asyncio
import requests
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from aiogram.filters import Command
from datetime import datetime, timedelta  # <-- ДЛЯ ЧАСУ


API_TOKEN = "7674406693:AAFm9VTyW9uANoM_8lLQldsILEHBxQcR68s"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ===== ЛОКАЛЬНИЙ СЛОВНИК ПОВНИХ НАЗВ МОНЕТ =====
COIN_NAMES = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "BNB": "BNB Chain",
    "SOL": "Solana",
    "XRP": "Ripple",
    "ADA": "Cardano",
    "DOT": "Polkadot",
    "DOGE": "Dogecoin",
    "TON": "TON",
    "TRX": "Tron",
    "MATIC": "Polygon",
    "LTC": "Litecoin",
    "STRK": "Starknet",
    "AVAX": "Avalanche",
    "ARB": "Arbitrum",
}


# ===== Завантаження логотипу локально + створення КРУГЛОЇ іконки =====
def get_coin_logo(symbol: str):
    try:
        path = f"icons/{symbol.lower()}.png"
        full_name = COIN_NAMES.get(symbol.upper(), symbol.upper())

        if not os.path.exists(path):
            print(f"⚠️ Локальна іконка не знайдена: {path}")
            return None, full_name

        logo = Image.open(path).convert("RGBA")
        logo = logo.resize((44, 44), Image.LANCZOS)

        mask = Image.new("L", (44, 44), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 44, 44), fill=255)

        circular_logo = Image.new("RGBA", (44, 44))
        circular_logo.paste(logo, (0, 0), mask)

        return circular_logo, full_name

    except Exception as e:
        print(f"❌ Logo load error: {e}")
        return None, COIN_NAMES.get(symbol.upper(), symbol.upper())


# ===== Генерація фінального зображення =====
def generate_full_image(coin_data):
    bg = Image.open("background.png").convert("RGBA")
    draw = ImageDraw.Draw(bg)

    # ==== Шрифти ====
    try:
        font_symbol = ImageFont.truetype("fonts/Roboto-Medium.ttf", 20)
        font_name = ImageFont.truetype("fonts/Roboto-Regular.ttf", 16)
        font_percent = ImageFont.truetype("fonts/Roboto-Medium.ttf", 21)
        font_time = ImageFont.truetype("fonts/Roboto-Medium.ttf", 24)  # ШРИФТ ЧАСУ
    except:
        font_symbol = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_percent = ImageFont.load_default()
        font_time = ImageFont.load_default()

    # ==== Стилі ====
    color_white = (255, 255, 255)
    color_gray = (150, 150, 150)
    color_green = (92, 174, 121)

    # ==============
    #     ЧАС МСК
    # ==============
    msk_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%H:%M")

    # Малюємо час у верхньому лівому куті
    draw.text((28, 20), msk_time, font=font_time, fill=color_white)


    # ==== Координати монет ====
    start_y = 310
    step_y = 89

    for idx, (symbol, percent) in enumerate(coin_data[:10]):
        y = start_y + idx * step_y
        x_logo = 20
        x_text = 90

        logo, full_name = get_coin_logo(symbol)
        if logo:
            bg.paste(logo, (x_logo, y + 10), logo)

        draw.text((x_text, y + 5), symbol.upper(), font=font_symbol, fill=color_white)
        draw.text((x_text, y + 40), full_name, font=font_name, fill=color_gray)

        percent_text = f"{percent:.2f}"
        font_mrp = ImageFont.truetype("fonts/Roboto-Medium.ttf", font_percent.size - 6)

        percent_width = draw.textlength(percent_text, font=font_percent)
        percent_symbol_width = draw.textlength('%', font=font_percent)
        mrp_width = draw.textlength('MRP', font=font_mrp)

        total_width = percent_width + 5 + percent_symbol_width + 5 + mrp_width
        right_margin = 564
        x_start = right_margin - total_width

        draw.text((x_start, y + 10), percent_text, font=font_percent, fill=color_green)

        x_percent = x_start + percent_width
        draw.text((x_percent, y + 10), "%", font=font_percent, fill=color_green)

        x_mrp = x_percent + percent_symbol_width + 5
        draw.text((x_mrp, y + 10 + (24 - 18)), "MRP", font=font_mrp, fill=color_green)

    output_path = "result_full.png"
    bg.save(output_path)
    return output_path


# ===== /start =====
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привіт! Надішли список монет у форматі:\n\n"
        "`1 BTC 5.12`\n"
        "`2 ETH 3.62`\n"
        "`3 SOL 7.22`\n\n"
        "🔹 максимум 10 рядків\n"
        "Бот створить один скрін з усіма монетами 💰",
        parse_mode="Markdown"
    )


# ===== Обробка введення =====
@dp.message()
async def handle_input(message: types.Message):
    try:
        lines = message.text.strip().split("\n")
        coin_data = []

        for line in lines[:10]:
            parts = line.strip().split()
            if len(parts) == 2:
                coin, percent = parts
            elif len(parts) == 3:
                _, coin, percent = parts
            else:
                continue

            try:
                percent = float(percent)
            except:
                continue

            coin_data.append((coin, percent))

        if not coin_data:
            await message.answer("⚠️ Не вдалося розпізнати монети.")
            return

        path = generate_full_image(coin_data)
        photo = FSInputFile(path)
        await message.answer_photo(photo)

    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")


# ===== Запуск =====
async def main():
    print("🤖 Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
