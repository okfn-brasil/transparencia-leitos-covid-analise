import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# this sets the python locale to pt_BR.UTF-8
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# # if you need to check for fonts
# matplotlib.font_manager._rebuild()
# from matplotlib.font_manager import findfont, FontProperties
# font = findfont(FontProperties(family=['IBM Plex Sans']))
# font

CHARTS_FOLDER = 'exports/charts'
STANDARD_FIGSIZE = (16,12)

OK_COLOR_SCALE_DIVERGING_COLORS = ['#00cb8d', '#99d9b1', '#eae4d6', '#e48fb0', '#d01c8c']
OK_COLOR_SCALE_DIVERGING = matplotlib.colors.LinearSegmentedColormap.from_list("", OK_COLOR_SCALE_DIVERGING_COLORS)
OK_PRIMARY = OK_COLOR_SCALE_DIVERGING_COLORS[0]

font_family = {'family':'IBM Plex Sans',
               'weight': 'regular',
              }

factor = 1
SMALL_SIZE = 12 * factor
MEDIUM_SIZE = 14 * factor
BIGGER_SIZE = 18 * factor

S_LABEL_PAD = 10
M_LABEL_PAD = S_LABEL_PAD * 2

plt.rc('font', size=SMALL_SIZE, **font_family)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def increase_chart_margins(plt, plot_margin=0.15):
    x0, x1, y0, y1 = plt.axis()
    plt.axis((x0 - plot_margin,
              x1 + plot_margin,
              y0 - plot_margin,
              y1 + plot_margin))

def remove_chart_spines(ax, spines=['top', 'right', 'bottom', 'left']):
    for spine in spines:
        ax.spines[spine].set_visible(False)


def set_ticks(ax):
    ax.tick_params(axis='both', which='major', labelsize=SMALL_SIZE)
    ax.tick_params(axis='both', which='minor', labelsize=SMALL_SIZE)


def set_grid_x(ax):
    ax.xaxis.grid(True, which='minor', zorder=-1, linestyle='-', linewidth=0)
    ax.xaxis.grid(True, which='major', zorder=-1, linestyle='-', linewidth=0.6)


def set_grid_y(ax):
    ax.yaxis.grid(True, which='major', zorder=-1, linestyle='-', linewidth=0.6)


def set_grid(ax):
    set_grid_x(ax)
    set_grid_y(ax)


def set_axis(ax):
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: str(x).replace('.', ',')))
    ax.xaxis.label.set_visible(True)


def default_chart_configs(ax):
    increase_chart_margins(plt)
    remove_chart_spines(ax)
    set_ticks(ax)
    set_grid(ax)
    set_axis(ax)


def plot_barh(df, metric_col,
              figsize=STANDARD_FIGSIZE, xlim_padding=1.1,
              facecolor='#f2f3f2', title='',
              ylabel='', xlabel='', annotate=True,
              xgrid=False, color=OK_PRIMARY,
              round_pct=False, ascending=True,
              file_format='png',
              file_name=None, charts_folder=CHARTS_FOLDER,
              **kwargs):
    df_tmp = df[metric_col].sort_values(ascending=ascending)
    if round_pct is True:
        df_tmp = round(df_tmp * 100, 1)
    fig, ax = plt.subplots(figsize=figsize)

    df_tmp.plot.barh(ax=ax, color=color, zorder=3)

    ax.set_xlim(0, round(df_tmp.max() * xlim_padding))
    ax.set_facecolor(facecolor)
    if xgrid is True:
        set_grid_x(ax)

    ax.invert_yaxis()
    ax.set_title(title, fontsize=BIGGER_SIZE, pad=M_LABEL_PAD)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.xaxis.labelpad = M_LABEL_PAD

    if annotate is True:
        for p in ax.patches:
            left, bottom, width, height = p.get_bbox().bounds
            label = str(round(width, 1))
            ax.annotate(label, xy=((left + width) + 0.5, bottom + height / 2),
                        ha='left', va='center')

    remove_chart_spines(ax)
    # set_ticks(ax)

    if file_name:
        ax.figure.savefig(f'{charts_folder}/{file_name}.{file_format}',
                          bbox_inches='tight', dpi=300, facecolor='#fff')


def plot_heatmap(df, metric_cols, cols_order=[],
              figsize=STANDARD_FIGSIZE, xlim_padding=1.1,
              facecolor='#bbbbbb', title='',
              ylabel='', xlabel='', annotate=True,
              xgrid=False, color=OK_COLOR_SCALE_DIVERGING,
              xticklabels=[], vmin=0, vmax=100,
              round_pct=False, legend='', legend_y=-0.15,
              cbar_ticks=[0, 50, 100],
              cbar_labels=[' 0%', ' 50%', ' 100%'],
              file_format='png',
              file_name=None, charts_folder=CHARTS_FOLDER,
              **kwargs):
    df_tmp = df[metric_cols]
    if round_pct is True:
        df_tmp = round(df_tmp * 100, 1)
    if cols_order:
        df_tmp = df_tmp.reindex(columns=cols_order)
    fig, ax = plt.subplots(figsize=figsize)

    sns.heatmap(df_tmp, annot=annotate, ax=ax, cmap=color, fmt='g', vmin=vmin, vmax=vmax, xticklabels=xticklabels)

    ax.set_facecolor(facecolor)
    ax.set_title(title, fontsize=BIGGER_SIZE, pad=M_LABEL_PAD)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.xaxis.labelpad = M_LABEL_PAD
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=12)

    for i in range(df_tmp.shape[0] + 1):
        ax.axhline(i, color='white', lw=3)
    for i in range(df_tmp.shape[1] + 1):
        ax.axvline(i, color='white', lw=3)

    cbar = ax.collections[0].colorbar
    cbar.set_ticks(cbar_ticks)
    cbar.set_ticklabels(cbar_labels)

    ax.text(0, legend_y, legend,
         horizontalalignment='left',
         verticalalignment='center',
         transform = ax.transAxes)

    if file_name:
        ax.figure.savefig(f'{charts_folder}/{file_name}.{file_format}',
                          bbox_inches='tight', dpi=300, facecolor='#fff')
