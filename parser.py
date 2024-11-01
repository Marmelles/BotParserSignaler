import requests
from bs4 import BeautifulSoup
import requests
import html
from urllib.parse import parse_qs
import re

from Helper import createAdrForMatchPattern

def get_game_info():
    countries_urls = {
        "Хорватия": "https://hos-web.dataproject.com/",
        "Бельгия": "https://bevl-web.dataproject.com/",
        "Венгрия": "https://hvf-web.dataproject.com/",
        "Сербия": "https://ossrb-web.dataproject.com/",
        "Греция": "https://hvl-web.dataproject.com/",
        "Болгария": "https://bvf-web.dataproject.com/",
        "Румыния": "https://frv-web.dataproject.com/",
        "Катар": "https://qva-web.dataproject.com/",
        "Швеция": "https://svbf-web.dataproject.com/",
        "Чехия": "https://cvf-web.dataproject.com/",
        "Словения": "https://ozs-web.dataproject.com/",
        "Турция": "https://tvf-web.dataproject.com/",
        "Норвегия": "https://nvbf-web.dataproject.com/",
        "Словакия": "https://svf-web.dataproject.com/",
        "Португалия": "https://fpv-web.dataproject.com/",
        "Испания": "https://rfevb-web.dataproject.com/",
        "Исландия": "https://bli-web.dataproject.com/",
        "Финляндия": "https://lml-web.dataproject.com/",
        "Франция": "https://lnv-web.dataproject.com/"
    }
    responseData = {}

    # страна : [страницы с статистикой матчей]
    siteWithMatches = {}
    # Проход по всем URL в словаре
    index = 0
    for country, url in countries_urls.items():
        try:
            if(index > 6):
                continue
            # Создаём Конечный УРЛ и отправляем запрос
            urlMain = url + 'MainLiveScore.aspx'
            response = requests.get(urlMain)
            response.raise_for_status()  # Проверка на ошибки HTTP

            # Поиск подстроки в HTML-коде
            matches = re.findall(r'MatchStatistics\.aspx\?(.*?);,', response.text)

            # По всем нахождениям идущих матчей
            if matches:
                # Создаём массив для хранения матчей страны
                siteWithMatches[country] = []
                for match in matches:
                    appendAddr = createAdrForMatchPattern(match)
                    siteWithMatches[country].append(appendAddr)
                    index += 1
                    print(appendAddr)

        except requests.exceptions.RequestException as e:
            print(f"{country}: Ошибка при обращении к {urlMain} - {e}")

    print('Первая половина обработки данных завершена ....')

    for country, arrayAppendAddr in siteWithMatches.items():
        responseData[country] = []
        for appendAddr in arrayAppendAddr:
            urlMain = countries_urls[country] + appendAddr
            print(appendAddr)
            response = requests.get(urlMain)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            objData = {}
            try:
                linkLive = soup.select_one('#Content_Main_a_live')['href']
            except:
                linkLive = ''

            # Извлечение части запроса
            query_part = appendAddr.split('?')[1]
            # Парсинг параметров запроса
            parsed_query = parse_qs(query_part)
            # Получение значения mID
            mID = parsed_query.get('mID', [None])[0]

            objData['mID'] = f"{mID}"
            objData['linkLive'] = f"{countries_urls[country]}/{linkLive}"
            toStr = f"{country}:  "
            #toStr = f"- Матч {index}  "
            #toStr += f"- [Матч {index}]({objData['linkLive']}) "

            team1 = ''
            team2 = ''
            time = ''

            try:
                team1 = soup.select_one('#Content_Main_LBL_HomeTeam').text
                team2 = soup.select_one('#Content_Main_LBL_GuestTeam').text
                timeNonFormater = soup.select_one('#Content_Main_LB_DateTime').text
                timeFormat = re.search(r'\b\d{1,2}:\d{2}\b', timeNonFormater)
                if(timeFormat != None):
                    time = timeFormat[0]
                else:
                    timeFormat = re.search(r'\b\d{1,2}.\d{2}\b', timeNonFormater)
                    if (timeFormat != None):
                        time = timeFormat[0]

                toStr += f" {team1} vs {team2} в {time}"

            except:
                toStr += 'Ошибка сбора данных'

            objData['team1'] = team1
            objData['team2'] = team2
            objData['time'] = time
            objData['toStr'] = toStr
            responseData[country].append(objData)

    return responseData

#asd = get_game_info()