import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile

from DB import add_match_info, initDB, get_record_DB, add_stalk_info
from parserNew import get_game_info
from parserSSE import load_page_and_get_players

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
    game_list = get_game_info()

    keyboard = []

    response_message = "Вот матчи что я нашёл) (Пока ограниченно до 3 стран)"
    for id, game_object in game_list.items():
        recordObj = {
            'mID': game_object['mID'],
            'nameCountry': game_object['nameCountry'],
            'urlCountry': game_object['urlCountry'],
            'nameTeam1': game_object['team1'],
            'nameTeam2': game_object['team2'],
            'idYear': game_object['yearID'],
        }
        add_match_info(recordObj)
        keyboard.append([InlineKeyboardButton(text=f"{game_object['nameCountry']}: {game_object['toStr']}", callback_data=f"=selectGame={id}")])

    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=keyboard)
    await query.message.answer(response_message, reply_markup=inline_keyboard, parse_mode='Markdown')
    #await query.answer()  # Чтобы закрыть индикатор загрузки

@dp.callback_query(lambda query: query.data.startswith("=selectGame="))
async def selectGame(query: types.CallbackQuery):
    id = query.data.replace('=selectGame=', '')
    gameInfo = get_record_DB('gameInfo', id)
    keyboard = []
    keyboard.append([InlineKeyboardButton(text=f"{gameInfo['nameTeam1']}", callback_data=f"=selectCommand=Home={id}")])
    keyboard.append([InlineKeyboardButton(text=f"{gameInfo['nameTeam2']}", callback_data=f"=selectCommand=Guest={id}")])

    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=keyboard)
    response_message = "Выберите команду)"
    await query.message.answer(response_message, reply_markup=inline_keyboard, parse_mode='Markdown')
    await query.answer()
@dp.callback_query(lambda query: query.data.startswith("=selectCommand="))
async def selectCommand(query: types.CallbackQuery):
    promt = query.data.replace('=selectCommand=', '')
    id = 0
    team = 'team'
    if(promt.__contains__('Home=')):
        id = promt.replace('Home=', '')
        team += '1'
    else:
        id = promt.replace('Guest=', '')
        team += '2'


    commandInfo = load_page_and_get_players(id)
    commandList = commandInfo[team]

    keyboard = []
    for player in commandList:
        keyboard.append([InlineKeyboardButton(text=f"{player['pNumber']} {player['pName']}", callback_data=f"=selectPlayer=mId={id}={player['pNumber']}")])

    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=keyboard)
    response_message = "Выберите игрока)"
    await query.message.answer(response_message, reply_markup=inline_keyboard, parse_mode='Markdown')
    #await query.answer()

@dp.callback_query(lambda query: query.data.startswith("=selectPlayer="))
async def selectCommand(query: types.CallbackQuery):
    promt = query.data.replace('=selectPlayer=', '')
    mId = promt.split('=')[1]
    pNumber = promt.split('=')[2]
    objAdd = {
        'mID': mId,
        'numberPlayer': pNumber,
        'idUser': query.from_user.id,
    }
    start = datetime.now()
    print(datetime.now())
    add_stalk_info(objAdd)
    print(datetime.now() - start)
    await query.message.answer('Игрок запомнен и теперь отслеживается его уход с  поля', parse_mode='Markdown')
    await query.answer()
@dp.callback_query()
async def handle_callback(query: types.CallbackQuery):
    await query.message.answer(f"Неизвестная команда ({query.data})")
    await query.answer()  # Чтобы закрыть индикатор загрузки

async def main():
    try:
        initDB()
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
