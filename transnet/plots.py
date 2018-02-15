import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import acf, pacf

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_ts(df):
    df.plot(figsize=(13, 8), subplots=False)
    plt.title('Timeseries')
    plt.savefig('plot_ts.png')


def plot_acf(timeseries):
    plt.figure(figsize=(13, 8))
    plt.title('Autocorrelation')
    lag_acf = acf(timeseries, nlags=14 * 24 * 4)
    plt.axvline(x=1 * 24 * 4, linestyle='--', color='gray')
    plt.axvline(x=7 * 24 * 4, linestyle='--', color='gray')
    # plt.axhline(y=1.96 / np.sqrt(len(df.loc[~df['residuals'].isnull(), 'residuals'])), linestyle='--', color='gray')
    plt.scatter(x=range(len(lag_acf)), y=list(lag_acf))
    plt.savefig('plot_acf.png')


def plot_pacf(timeseries):
    plt.figure(figsize=(13, 8))
    plt.title('Partial Autocorrelation')
    lag_pacf = pacf(timeseries, nlags=24 * 4)
    # plt.axhline(y=1.96 / np.sqrt(len(df.loc[~df['residuals'].isnull(), 'residuals'])), linestyle='--', color='gray')
    plt.scatter(x=range(len(lag_pacf)), y=list(lag_pacf))
    plt.savefig('plot_pacf.png')


def plot_evaluate(plots):
    plt.figure(figsize=(13, 8))
    plt.title('Evaluation')
    for color, plot in plots.items():
        plt.plot(plot, color=color)
    plt.savefig('plot_evaluation.png')
