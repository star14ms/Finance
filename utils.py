from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import re
import json
from rich import print
from datetime import datetime, timedelta, timezone
from requests import get
from requests import Response
from rich_ import print_html


EST = timezone(timedelta(hours=0)) # UTC-5 뉴욕 (EST), UTC+9 대한민국 (KST)


def get_html_soup(url: str):
    try:
        html = urlopen(url)
    except:
        from requests import get
        response = get(url)
        html = response._content
    soup = bs(html, "html.parser")
    return soup


class GoogleFinance:

    @staticmethod
    def _extract_data(soup: bs):
        p = re.compile('{.*}', re.DOTALL)
        p2 = re.compile(r"'(\w+):")
        p3 = re.compile(r'"(\w+):')
        p4 = re.compile(r"(\w+):")
        
        info = p.findall(soup)[0]
        info = re.sub(p2, r"'\1-", info)
        info = re.sub(p3, r'"\1-', info)
        info = re.sub(p4, r'"\1":', info)
        info = info.replace('\n','').replace("'",'"')
    
    
        info = dict(json.loads(info))
        info = info.get('data')
    
        return info
    
    @staticmethod
    def _data_to_dict(data: list):
        data = data[0][0]
        _data = [stock_price for stock_prices in data[3] for stock_price in stock_prices[1]]
        stocks = [x[1][0] for x in _data]
        volumes = [x[2] for x in _data if len(x) > 2]

        is_long_term_chart = _data[0][0][2] != _data[len(_data)//2][0][2]    
        strftime_format = '%m-%d' if is_long_term_chart else '%H:%M'
        dates = [datetime(
            year=x[0][0] if x[0][0] is not None else 0, 
            month=x[0][1] if x[0][1] is not None else 0, 
            day=x[0][2] if x[0][2] is not None else 0,
            hour=x[0][3] if x[0][3] is not None else 0,
            minute=x[0][4] if x[0][4] is not None else 0,
        ).strftime(strftime_format) if idx % max(1, min(1000, (len(_data) // 20))) == 0 else '' for idx, x in enumerate(_data)]

        stock_info = {
            'money': data[2],
            'company': data[7],
            'stocks': stocks,
            'volumes': volumes,
            'dates': dates,
        }

        return stock_info
    
    @staticmethod
    def request_stock_data(
        quote: str, 
        window: str = '1D',
        search_url: str = 'https://www.google.com/finance/quote/', 
        stock_selector: str = 'div.kf1m0', 
    ):
        '''
        Parameters
        --------
        window: 
            >>> '1D' | '5D' | '1M' | '6M' | 'YTD' | '1Y' | '5Y' | 'MAX'
        '''
    
        soup = get_html_soup(search_url + quote + '?comparison=&window=' + window)
        soup_set = soup.find_all('script')

        # jsdata = soup.select_one('c-wiz')['jsdata']
        # print(jsdata)
        
        # stock = soup.select_one(stock_selector).text
        # idx = find_script_idx_has_stock_info(soup, stock.split('.')[0][1:])
    
        data_list = []

        sep = ':' if ':' in quote else '-'
    
        for idx, s in enumerate(soup_set):
            soup = str(s)
            if 'data' in soup and quote.split(sep)[0] in soup and quote.split(sep)[1] in soup:
                try:
                    data = GoogleFinance._extract_data(soup)

                    if len(data[0][0]) >= 10:
                        data_list.append(GoogleFinance._data_to_dict(data))
    
                except:
                    pass
        
        return data_list


class GoogleSearch:
    @staticmethod
    def _get_company_mid_company_name(quote, search_url: str = 'https://www.google.com/finance/quote/'):
        soup = get_html_soup(search_url + quote)
        el = soup.select('.Gfxi4')[-1]
        el = el.select_one('div c-wiz div div div')
        mid = el.get('data-mid')

        company = soup.select_one('.zzDege').text

        return mid, company

    @staticmethod
    def _extract_data(response: Response):
        p = re.compile(r'[[]{3}(.*)[]]{3}')
        data = p.findall(response.text)[0]
        data = '[[[' + data + ']]]'
        data = json.loads(data)
        data = data[0][0][1]
        data = json.loads(data)
    
        return data
    
    @staticmethod
    def _data_to_dict(data: list):
        money = data[3][0]
        data = data[0][3][0][0]
        stocks = [data_one[2][0][0] for data_one in data[0][0]]

        jump = 2
        for idx, stock in enumerate(stocks[:]):
            if not (-1+jump < idx < len(stocks)-jump):
                continue

            b_stock = stocks[idx-jump]
            a_stock = stocks[idx+jump]

            # if sd * min_sd_times_not_wrong_data < abs(stock - avg):
            if (abs(b_stock - stock) > b_stock*0.2 or abs(a_stock - stock) > a_stock*0.2) and \
                abs(b_stock - a_stock) < b_stock*0.2:
                stocks[idx] = b_stock
                print(stock, '=>', b_stock)

        period_day = (data[0][0][-1][5] - data[0][0][0][5]) / 1440
        dates = [
            number2datetime(data_one[5]).strftime(
                '%H:%M' if period_day <= 1 else '%m-%d %H:%M' if 1 < period_day <= 10 else '%m-%d'
            )
            if idx % max(1, min(1000, len(data[0][0]) // 20)) == 0 else '' 
                for idx, data_one in enumerate(data[0][0])
        ]
        # aftermarket = data[1]

        stock_info = {
            'company': '',
            'money': money,
            'stocks': stocks,
            'volumes': None,
            'dates': dates,
        }
    
        return stock_info
    
    @staticmethod
    def request_stock_data(
        quote: str, 
        period: str = '1d',
        search_url: str = 'https://www.google.co.kr/async/finance_wholepage_chart?', 
    ):
        '''
        Parameters
        --------
        period: 
            >>> '1d' | '5d' | '1M' | '6M' | 'YTD' | '1Y' | '5Y' | 'MAX'
        '''

        mid, company = GoogleSearch._get_company_mid_company_name(quote)
        interval = 60 if period in ['1d'] else 300 if period in ['5d', '1M'] else 1800 if period in ['6M'] else 86400
        extended = 'true' if period=='1d' else 'false'

        url = search_url + \
            f'&yv=3&cs=1&async=mid_list:{mid},period:{period},interval:{interval},extended:{extended},_pms:s,_fmt:pc'

        response = get(url)
        data = GoogleSearch._extract_data(response)
        data_dict = GoogleSearch._data_to_dict(data)
        data_dict['company'] = company
        
        return [data_dict]


class FinanceDataRequestManager:
    def __init__(self, method: str) -> None:
        if method == 'google-finance':
            self.method = GoogleFinance
        elif method == 'google-search':
            self.method = GoogleSearch
        else:
            raise 'undefined request method'
    
    def request(self):
        return self.method.request_stock_data()


def number2datetime(number: int):
    start = datetime(1970, 1, 1, tzinfo=EST)
    _datetime = start + timedelta(minutes=number)

    return _datetime
