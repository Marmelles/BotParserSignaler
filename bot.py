import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile

from DB import add_match_info, initDB, get_record_DB, add_stalk_info, get_playerInfo_DB, get_all_stalk_DB, del_stalk_DB
from parserNew import get_game_info
from parserSSE import load_page_and_get_players, infinityParsing

API_TOKEN = '7596556749:AAEvIdEDAtAwDipl14EuiVDWbcwk61XYbtY'
initDB()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Добавляем команды в меню
async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Запустить бота | Главное меню")
    ]
    await bot.set_my_commands(commands)

async def unlockButton(query):
    try:
        await query.answer()  # Чтобы закрыть индикатор загрузки
    except:
        pass
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_name = message.from_user.first_name  # Имя пользователя
    gif_path = 'media/welcome.gif'  # Относительный путь к GIF

    # Создаем обычные кнопки под полем ввода
    keyboard = [
        [InlineKeyboardButton(text="Какие игры скоро будут или уже идут?", callback_data="game_list")],
        [InlineKeyboardButton(text="Кто сейчас отслеживается?", callback_data="stalk_list")],
          # Две кнопки в одной строке
    ]
    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=keyboard)

    # Отправляем сообщение с обычными кнопками
    gif_file = FSInputFile(gif_path)
    await message.answer_animation(animation=gif_file, caption=f"👋 Рад видеть тебя, @{user_name}", reply_markup=inline_keyboard)

# Хэндлер для обработки нажатий на инлайн-кнопки
@dp.callback_query(lambda query: query.data == "stalk_list")
async def stalk_list(query: types.CallbackQuery):
    stalkList = get_all_stalk_DB(query.from_user.id)
    keyboard = []
    for stalk in stalkList:
        text = f'{stalk['nameCountry']}: {stalk['nameTeam1']} vs {stalk['nameTeam2']} -> {stalk['numberPlayer']} {stalk['namePlayer']}'
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"=delStalk={stalk['id']}")])

    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=keyboard)
    mainText = ('*Вот игроки за которыми вы сейчас следите:* \n'
                'Клик по кнопке запустит удаление слежки за данным игроком')

    if len(keyboard) == 0:
        mainText = 'Пока вы никого не отслеживаете в матчах'

    await query.message.answer(mainText, reply_markup=inline_keyboard, parse_mode='Markdown')
    await unlockButton(query)
@dp.callback_query(lambda query: query.data.startswith("=delStalk="))
async def delStalk(query: types.CallbackQuery):
    id = query.data.replace('=delStalk=', '')
    delInfo = del_stalk_DB(id)
    text = (f'Игрок *{delInfo['numberPlayer']} {delInfo['namePlayer']}* больше не отслеживается '
            f'в матче {delInfo['nameCountry']}: *{delInfo['nameTeam1']}* vs *{delInfo['nameTeam2']}*')
    await query.message.answer(text=text, parse_mode='Markdown')
    await unlockButton(query)
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
    await unlockButton(query)  # Чтобы закрыть индикатор загрузки


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
    await unlockButton(query)
@dp.callback_query(lambda query: query.data.startswith("=selectCommand="))
async def selectCommand(query: types.CallbackQuery):
    promt = query.data.replace('=selectCommand=', '')
    id = 0
    team = 'team'
    teamCom = 'Home'
    if(promt.__contains__('Home=')):
        id = promt.replace('Home=', '')
        teamCom = 'Home'
        team += '1'
    else:
        id = promt.replace('Guest=', '')
        teamCom = 'Guest'
        team += '2'

    dataDB = get_record_DB('gameInfo', id)
    #print(dataDB['urlCountry'])
    commandList = load_page_and_get_players(id, dataDB['urlCountry'])[team]

    keyboard = []
    arrayButton = []
    for player in commandList:
        arrayButton.append(InlineKeyboardButton(text=f"{player['pNumber']} {player['pName']}",
                                                callback_data=f"=SelPl=mId={id}={player['pNumber']}={teamCom}"))
        if(len(arrayButton) == 2):
            keyboard.append(arrayButton)
            arrayButton = []

    if(len(arrayButton) != 0):
        keyboard.append(arrayButton)

    inline_keyboard = InlineKeyboardMarkup(row_width=2, inline_keyboard=keyboard)
    response_message = "Выберите игрока:"
    await query.message.answer(response_message, reply_markup=inline_keyboard, parse_mode='Markdown')
    await unlockButton(query)

@dp.callback_query(lambda query: query.data.startswith("=SelPl="))
async def selectCommand(query: types.CallbackQuery):
    promt = query.data.replace('=SelPl=', '')
    mId = promt.split('=')[1]
    pNumber = promt.split('=')[2]
    teamCom = promt.split('=')[3]

    dataDB = get_record_DB('gameInfo', mId)
    objAdd = {
        'mID': mId,
        'numberPlayer': pNumber,
        'idUser': query.from_user.id,
        'urlCountry': dataDB['urlCountry'],
        'teamCom': teamCom,
    }

    result = add_stalk_info(objAdd)
    playerInfo = get_playerInfo_DB(mId, pNumber, teamCom)
    text = f'Игрок с номером {pNumber} запомнен и теперь отслеживается!'
    if playerInfo is not None:
        text = f'Игрок *{playerInfo['numberPlayer']} {playerInfo['namePlayer']}* теперь отслеживается!'

    if(len(result) > 0):
        text = f'Игрок с номером {pNumber} {result}'

    await query.message.answer(text, parse_mode='Markdown')
    await unlockButton(query)
@dp.callback_query()
async def handle_callback(query: types.CallbackQuery):
    await query.message.answer(f"Неизвестная команда ({query.data})")
    await query.answer()  # Чтобы закрыть индикатор загрузки

# Функция для периодического выполнения
async def periodic_task():
    while True:
        result = infinityParsing()
        if len(result) > 0:  # Если результат не пустой
            for data in result:
                matchInfo = get_record_DB('gameInfo', data['mID'])
                text = (f"в Игре *{matchInfo['nameCountry']}*: *{matchInfo['nameTeam1']}* vs *{matchInfo['nameTeam2']}* \n"
                        f"Игрок *{data['pNumber']} {data['pName']}* не найден на поле")
                await bot.send_message(data['idUser'], text, parse_mode='Markdown')
        await asyncio.sleep(60)  # Пауза в 60 секунд
async def main():
    try:
        initDB()
        loop = asyncio.get_event_loop()
        loop.create_task(periodic_task())
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
