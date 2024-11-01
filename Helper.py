import requests
from bs4 import BeautifulSoup
import requests
import html
import re

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