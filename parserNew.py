from bs4 import BeautifulSoup
import requests
import re

from Helper import createAdrForMatchPattern, get_param_for_addr, get_text_soup


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
            if(index > 2):
                continue
            # Создаём Конечный УРЛ и отправляем запрос
            urlMain = url + 'MainLiveScore.aspx'
            response = requests.get(urlMain)
            response.raise_for_status()  # Проверка на ошибки HTTP
            soup = BeautifulSoup(response.text, 'html.parser')

            # Поиск подстроки в HTML-коде
            matches = re.findall(r'MatchStatistics\.aspx\?(.*?);,', response.text)
            #Если не нашли ничего выходим
            if matches is None:
                continue
            # По всем нахождениям идущих матчей
            for match in matches:
                appendAddr = createAdrForMatchPattern(match)
                mID = get_param_for_addr(appendAddr, 'mID')
                yearID = get_param_for_addr(appendAddr, 'ID')
                MatchStatistics = appendAddr
                time = get_text_soup(soup, f'#Content_Main_RLV_MatchList_LB_Ora_Today_{mID}')
                team1 = get_text_soup(soup, f'#Content_Main_RLV_MatchList_Label1_{mID}')
                team2 = get_text_soup(soup, f'#Content_Main_RLV_MatchList_Label2_{mID}')
                toStr = f"{team1} vs {team2} в {time}"

                responseData[mID] = {
                    'urlCountry': url,
                    'nameCountry': country,
                    'MatchStatistics': MatchStatistics,
                    'mID': mID,
                    'yearID': yearID,
                    'time': time,
                    'team1': team1,
                    'team2': team2,
                    'toStr': toStr
                }
                index += 1
                #print(appendAddr)


        except requests.exceptions.RequestException as e:
            print(f"{country}: Ошибка при обращении к {urlMain} - {e}")

    return responseData


