from rich import print
from rich.progress import track

from rich_ import print_html
from utils import FinanceDataRequestManager
from plot import plot_stock_chart_all


quotes = [
    'PYPL:NASDAQ',
    'CPNG:NYSE',
    'RBLX:NYSE',
    'TSLA:NASDAQ',
    '.IXIC:INDEXNASDAQ',
    # 'USD-KRW',
]

# request_manager = FinanceDataRequestManager('google-finance')
request_manager = FinanceDataRequestManager('google-search')

data_lists = []

for quote in track(quotes):
    data_list = request_manager.method.request_stock_data(quote, '1d')
    data_lists.append(data_list)

for i in range(0, len(data_lists), 4):
    i_cut = i+4 if i+4 < len(data_lists) else len(data_lists)
    plot_stock_chart_all(data_lists[i:i_cut], scale='linear', animation=False, dark_mode=True)

input()