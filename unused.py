from urllib.parse import quote_plus
from bs4 import ResultSet
import re

from utils import get_html_soup


def find_script_idx_has_stock_info(soup_set: ResultSet, text: str):
    max_count = 0
    idx_max_count = 0

    for idx, s in enumerate(soup_set):
        count = str(s).count(text)
        if max_count <= count:
          idx_max_count = idx
          max_count = count
    
    return idx_max_count


def get_company_ei_value(quote: str, base_url: str = 'https://www.google.co.kr/search?q='):
    url = f'{base_url}{quote_plus(quote)}'
    soup = get_html_soup(url)

    ei_info_el = str(soup.select_one('noscript'))
    p = re.compile(r'sei=((\w|-)+)')
    ei = p.findall(ei_info_el)[0]
    # ei = re.sub(p, r'\1', ei_info_el)

    return ei


# quote = '로블록스 주가'
# ei = get_company_ei_value(quote)
# print(ei)


def standard_deviation(numbers: list):
    average = sum(numbers) / len(numbers)

    sum_deviation = 0
    for number in numbers:
      deviation = number - average
      sum_deviation += deviation ** 2
    variance = sum_deviation / len(numbers)

    return variance ** 0.5
