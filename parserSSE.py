from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

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

def load_page_and_get_players(mID):
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
        driver.get(f"https://hos-web.dataproject.com/LiveScore_adv.aspx?ID={mID}")
        time.sleep(5)  # настройте время ожидания

        team1 = get_players_in_match(driver, 'Home')
        team2 = get_players_in_match(driver, 'Guest')

        players_in_match['team1'] = team1
        players_in_match['team2'] = team2

    finally:
        driver.quit()

    return players_in_match

data = load_page_and_get_players('6578')
#print(data)
