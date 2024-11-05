from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

from DB import get_record_DB, get_all_record_DB, del_record_DB
from Helper import get_element_driver


def get_players_in_match(driverRef, team):
    players_in_team = []
    data_elements = driverRef.find_elements(By.CLASS_NAME, f"LSA_DIV_Roster{team}_PlayerNumber")
    for element in data_elements:
        number = element.text
        id = element.get_attribute('id').replace(f'GV_Roster{team}_DIV_RosterPlayerNumber_', '')
        name = get_element_driver(driverRef, f"GV_Roster{team}_LBL_Roster{team}PlayerName_{id}")
        type = 'zapas'
        playerObj = {
            'pID': id,
            'pName': name,
            'pType': type,
            'pNumber': number,
        }
        players_in_team.append(playerObj)

    for index in range(6):
        indexPlayer = index + 1
        number = get_element_driver(driverRef, f"{team}{indexPlayer}")
        if(number == ''):
            continue

        name = get_element_driver(driverRef, f"{team}{indexPlayer}PlayerName")
        type = 'inGame'
        playerObj = {
            'pName': name,
            'pType': type,
            'pNumber': number,
        }
        players_in_team.append(playerObj)

    return players_in_team

def load_page_and_get_players(mID, urlCountry):
    # Инициализация браузера с помощью webdriver-manager
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=options)

    players_in_match = {
        'team1': [],
        'team2': []
    }

    try:
        # Ваш код для загрузки и парсинга страницы
        print(urlCountry)
        driver.get(f"{urlCountry}/LiveScore_adv.aspx?ID={mID}")
        time.sleep(5)  # настройте время ожидания

        team1 = get_players_in_match(driver, 'Home')
        team2 = get_players_in_match(driver, 'Guest')

        players_in_match['team1'] = team1
        players_in_match['team2'] = team2

    finally:
        driver.quit()

    return players_in_match




def infinityParsing():
    dataDB = get_all_record_DB('stalkPlayerInGame')

    if len(dataDB) == 0:
        return
    signalRecord = []
    for record in dataDB:
        mID = record['mID']
        numberPlayer = record['numberPlayer']
        urlCountry = record['urlCountry']

        commandInfo = load_page_and_get_players(mID, urlCountry)
        arrayPlayers = commandInfo['team1'] + commandInfo['team2']

        in_game_count = len(list(filter(lambda obj: obj['pType'] == 'inGame', arrayPlayers)))
        if in_game_count == 0:
            #continue
            pass

        has_player = any(filter(lambda obj: obj['pNumber'] == numberPlayer and obj['pType'] == 'inGame', arrayPlayers))

        if has_player == False:
            del_record_DB('stalkPlayerInGame', mID)
            signalRecord.append(record)

    return signalRecord

