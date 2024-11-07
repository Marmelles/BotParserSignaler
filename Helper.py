
import html
from urllib.parse import parse_qs
import re
from selenium.webdriver.common.by import By


def createAdrForMatchPattern(match):
    adr = html.unescape(f"MatchStatistics.aspx?{match}")

    # Удаляем символ ' в конце строки
    adr = adr.rstrip("'")

    # Регулярное выражение для удаления параметров CID и PID
    # Удаляем &CID=<число> и &PID=<число>, где <число> может быть любым
    cleaned_adr = re.sub(r'(&CID=\d+|&PID=\d+)', '', adr)

    # Удаляем лишние символы, если они остались
    cleaned_adr = cleaned_adr.replace('&&', '&').strip('&')

    # Удаляем ? если больше нет параметров
    if '?' in cleaned_adr and cleaned_adr.endswith('?'):
        cleaned_adr = cleaned_adr[:-1]
    return cleaned_adr


def get_param_for_addr(address, param_name):
    # Извлечение части запроса
    query_part = address.split('?')[1]
    # Парсинг параметров запроса
    parsed_query = parse_qs(query_part)
    # Получение значения mID
    find = parsed_query.get(param_name, [None])
    if find is None:
        return None
    return find[0]


def get_text_soup(soup, selector):
    data = soup.select_one(selector)
    data = data.text if data is not None else 'errorData'
    return data


def get_element_driver(driver, selector):
    try:
        data = driver.find_element(By.ID, selector)
        return data.text
    except:
        return ''



