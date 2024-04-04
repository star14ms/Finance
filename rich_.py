from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.traceback import install
from bs4 import BeautifulSoup as bs
from rich.text import Text
from rich import print
install()


console = Console(record=False)


def save_log(path='log.html'):
    console.save_html(path)


def new_progress():
    progress = Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )

    return progress


def print_html(soup):
    if not isinstance(soup, bs):
        soup = bs(str(soup), "html.parser")

    syntax = Syntax(soup.prettify(), "html", theme="monokai", line_numbers=True, dedent=True, word_wrap=False)
    console.print(syntax)




def getattrs_and_print_all(something):
    """특정 개체가 가지고 있는 모든 속성에 접근해본다."""
    
    for attr_name in dir(something):
        try:
            attr = getattr(something, attr_name)
            attr_name_str = Text(f'~.{attr_name}')

            if callable(attr):
                print(Syntax(f'{attr_name_str} = {attr()}', "python", theme="monokai", word_wrap=True))
            elif attr is None:
                print(Syntax(f'{attr_name_str} = {None}', "python", theme="monokai", word_wrap=True))
            else:
                print(Syntax(f'{attr_name_str} = {attr}', "python", theme="monokai", word_wrap=True))
        except:
            pass


if __name__ == '__main__':
    from rich.table import Table
    from rich.align import Align
    from rich.progress_bar import ProgressBar
    from rich.live import Live
    import time

    bar = ProgressBar(width=100, total=1)
    table = Table('n', 'n**2', 'n**3')
    table_centered = Align.center(table)

    live = Live(
        table, console=console, screen=False, 
        refresh_per_second=4, vertical_overflow="visible"
    )

    total = 1000

    with live:
        for i in range(1, total+1):
            bar.update(bar.completed + 1, total)
            table.caption = bar
            table.add_row(f"{i}", f"{i**2}", f"{i**3}")
            time.sleep(0.1)