import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, WebAppInfo

from parser import get_game_info

API_TOKEN = '7596556749:AAEvIdEDAtAwDipl14EuiVDWbcwk61XYbtY'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Добавляем команды в меню
async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Запустить бота | Главное меню")
    ]
    await bot.set_my_commands(commands)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_name = message.from_user.first_name  # Имя пользователя
    gif_path = 'media/welcome.gif'  # Относительный путь к GIF

    # Создаем обычные кнопки под полем ввода
    keyboard = [
        [InlineKeyboardButton(text="Какие игры скоро будут или уже идут?", callback_data="game_list")],
          # Две кнопки в одной строке
    ]
    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=keyboard)

    # Отправляем сообщение с обычными кнопками
    gif_file = FSInputFile(gif_path)
    await message.answer_animation(animation=gif_file, caption=f"👋 Рад видеть тебя, @{user_name}", reply_markup=inline_keyboard)

# Хэндлер для обработки нажатий на инлайн-кнопки
@dp.callback_query(lambda query: query.data == "game_list")
async def game_list(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id, text="Запрос принят, пожалуйста, подождите...")
    game_urls = get_game_info()

    keyboard = []

    response_message = "Вот матчи что я нашёл) (Пока ограниченно до 7 матчей)"
    for country, game_array in game_urls.items():
        for game_info in game_array:
            keyboard.append([InlineKeyboardButton(text=f"{game_info['toStr']}", callback_data=f"mID={game_info['mID']}")])

    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=keyboard)
    await query.message.answer(response_message, reply_markup=inline_keyboard, parse_mode='Markdown')
    #await query.answer()  # Чтобы закрыть индикатор загрузки

@dp.callback_query(lambda query: query.data.startswith("mID="))
async def selectGame(query: types.CallbackQuery):
    mID = query.data .replace('mID=', '')
    mID = int(mID)
    response_message = f'Пока тут пусто, но мы работаем над этим) ({mID})'
    await query.message.answer(response_message, parse_mode='Markdown')
@dp.callback_query()
async def handle_callback(query: types.CallbackQuery):
    await query.message.answer(f"Неизвестная команда")
    await query.answer()  # Чтобы закрыть индикатор загрузки

async def main():
    try:
        await set_commands(bot)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Polling error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
