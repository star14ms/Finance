import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.figure as Figure
from matplotlib.animation import FuncAnimation
import matplotlib.lines as lines
import numpy as np
import math
from datetime import datetime
from typing import List


colors = [ 
    '#17becf', '#7f7f7f',
]

dflt_cycle = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
    '#bcbd22', '#17becf'
] # dflt_cycle # ad[0].get_color() 


def plot_stock_chart(stocks: List[float|int], volumes: List[int] | None, dates: List[datetime] | None, company: str, money: str, fig: Figure, nrows: int, ncols: int, index: int, blank=False, dark_mode=False, scale='log'):
    ax = fig.add_subplot(nrows, ncols, index)

    len_data = len(stocks)
    if dark_mode: 
        ax.set_facecolor('xkcd:dark gray')
    
    if volumes is not None and sum(volumes) == 0:
        volumes = None
    if volumes is not None:
        twin2 = ax.twinx()
        twin2.set_ylim(0, max(volumes)*4)
    if blank:
        line, = ax.plot([], [], color=colors[0], label='주가($)')
        line2, = twin2.plot([], [], color=colors[1], label='거래량') if volumes else (None,)
    else:
        line, = ax.plot(np.arange(1, len_data+1), stocks, color=colors[0], label='주가($)')
        line2, = twin2.plot(np.arange(1, len_data+1), volumes, color=colors[1], label='거래량') if volumes else (None,)
    
    if dates is not None:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.set_xticklabels([''] + dates, rotation=45, size=14)

    # ax.xaxis.set_major_locator(ticker.MaxNLocator(20))
    # ticks_loc = ax.get_xticks().tolist()
    # ax.xaxis.set_major_locator(ticker.FixedLocator(ticks_loc))
    # ax.set_xticklabels([x for x in ticks_loc])

    for xtick in enumerate(ax.xaxis.majorTicks):
        if isinstance(xtick, tuple):
            if xtick[1].label1._text == '':
                xtick[1].gridline._alpha = 0
        elif xtick.label1._text == '':
            xtick.gridline._alpha = 0

    ax.set_title(company, fontdict={
        'size': 28,
        'color': 'white' if dark_mode else 'black',
    })
    ax.legend(handles=[line, line2] if volumes else [line], loc='best')
    ax.grid(True)
    ax.set_xmargin(0)
    if scale == 'log':
        ax.set_yscale('log', base=10)
        # ax.semilogy()
        ax.set_yticks([10**times for times in np.arange(0, 4, 1)])
        ax.set_ylim(0, 1000)
    else:
        ax.set_ylim(min(stocks)*0.99, max(stocks)*1.01)

    ax.yaxis.set_minor_formatter(ticker.ScalarFormatter())
    ax.set_xlim(1, len_data)
    # ax.set_xlabel('시간')
    # ax.set_ylabel(f'주가 ({money})')

    if not blank:
        return None
    elif volumes is None:
        return [(line, stocks)]
    else:
        return [(line, stocks),(line2, volumes)]


def plot_stock_chart_all(data_lists: list, scale: str = 'log', animation: bool = False, dark_mode: bool = False):
    plots_list = []
    ncols = max(1, int(len(data_lists) ** (1/2)))
    nrows = int(math.ceil(len(data_lists) / ncols))
    
    if len(data_lists[0]) > 1:
        data1 = data_lists[0][0]['stocks']
        data2 = data_lists[0][1]['stocks']
        standard_data = data1 if len(data1) > len(data2) else data2
    else:
        standard_data = data_lists[0][0]['stocks']
    
    if dark_mode:
        WHITE = 'white'
        # plt.rcParams['text.color'] = WHITE
        plt.rcParams['axes.labelcolor'] = WHITE
        plt.rcParams['xtick.color'] = WHITE
        plt.rcParams['ytick.color'] = WHITE

    for window in range(len(data_lists[0])):
        fig = plt.figure()
        if dark_mode:
            fig.patch.set_facecolor('xkcd:black')
        plt.subplots_adjust(left=0.04, right=0.97, bottom=0.08, top=0.95, hspace=0.28)
        plt.rcParams['font.size'] = 18

        for idx, data_list in enumerate(data_lists):
            i = 0
            # print(len(standard_data), len(data_list[0]['stocks']))
            if len(data_lists[0]) > 1:
                if -1 < len(standard_data) - len(data_list[0]['stocks']) < +1:
                    i = 0 if window == 0 else 1
                else:
                    i = 1 if window == 0 else 0

            if animation:
                plots = plot_stock_chart(**data_list[i], fig=fig, nrows=nrows, ncols=ncols, index=idx+1, blank=True, dark_mode=dark_mode, scale=scale)
                plots_list.append(plots)
            else:
                plot_stock_chart(**data_list[i], fig=fig, nrows=nrows, ncols=ncols, index=idx+1, dark_mode=dark_mode, scale=scale)
        
        if animation:
            len_data = len(data_list[i]['stocks'])
            anim = animate_plot(fig, plots_list, len_data)
        
        plt.get_current_fig_manager().full_screen_toggle()
        plt.show(block=False)


def animate_plot(fig: Figure, plots_list: list[lines.Line2D], len_data: int,
    video_time_sec=5, save=False, save_path='train_sprial_dataset_250ms.gif'
):
    n_frame_skip = 0
    interval = 0
    while interval < 100: # 최소 0.1초에 한 번 업데이트
        n_frame_skip += 1
        interval = math.ceil(video_time_sec*1000 / len_data * n_frame_skip)
    
    # print('interval', interval)
    
    def animate(i):
        until = n_frame_skip*i+1 if n_frame_skip*i+1 < len_data else len_data
        x = np.arange(1, until+1)
        for plots in plots_list:
            for plot, data in plots:
                plot.set_data(x, data[:until])
    
    anim = FuncAnimation(
        fig, animate, frames=len_data, 
        interval=interval, repeat=True, repeat_delay=3000,
    )
    
    if save:
        anim.save(save_path, writer='imagemagick')
    
    return anim


def set_font(font_path='', family=''):
    '''
        ``import matplotlib as mpl``
        
        ``print(mpl.matplotlib_fname())`` 이 경로에 폰트 추가 필요
        ``print(mpl.get_cachedir())`` 캐시 지우는 경로
    '''
    import matplotlib.font_manager as fm

    if family:
        font_name = family
    else:
        font_name = fm.FontProperties(fname=font_path, size=50).get_name()
    
    plt.rc('font', family=font_name)


set_font('NanumGothicExtraBold.ttf')
