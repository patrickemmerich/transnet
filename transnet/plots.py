import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import acf, pacf
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_ts(df):
    df.plot(figsize=(13, 8), subplots=False)
    plt.title('Timeseries')
    plt.savefig('plot_ts.png')


def plot_acf(timeseries):
    plt.figure(figsize=(6, 6))
    plt.title('Autocorrelation (ACF)')
    lag_acf = acf(timeseries, nlags=4 * 24 * 4)
    plt.axhline(y=1.96 / np.sqrt(len(timeseries)), linestyle='--', color='gray')
    plt.axhline(y=-1.96 / np.sqrt(len(timeseries)), linestyle='--', color='gray')
    plt.scatter(x=range(len(lag_acf)), y=list(lag_acf))
    plt.savefig('plot_acf.png')


def plot_pacf(timeseries):
    plt.figure(figsize=(6, 6))
    plt.title('Partial Autocorrelation (PACF)')
    lag_pacf = pacf(timeseries, nlags=60)
    plt.axhline(y=1.96 / np.sqrt(len(timeseries)), linestyle='--', color='gray')
    plt.axhline(y=-1.96 / np.sqrt(len(timeseries)), linestyle='--', color='gray')
    plt.axvline(x=2, linestyle='--', color='gray')
    plt.scatter(x=range(len(lag_pacf)), y=list(lag_pacf))
    plt.savefig('plot_pacf.png')


def plot_evaluate_ts(df):
    df.plot(figsize=(13, 8), subplots=False)
    plt.title('Evaluation')
    plt.savefig('plot_evaluation_ts.png')


def plot_evaluate_scatter(df):
    # supress large outliers (ok for a first approx, these outliers happen in both predictions)
    df = df.loc[(df['mae_pred_transnet'] < 600) & (df['mae_pred'] < 600)]

    plt.figure(figsize=(6, 6))
    x = df['mae_pred_transnet'].values
    y = df['mae_pred'].values
    plt.xlabel('mae_prediction_transnet')
    plt.ylabel('mae_prediction')
    plt.scatter(x, y)

    min_ = min(np.min(x), np.min(y)) - 10
    max_ = max(np.max(x), np.max(y)) + 10
    # draw diagonal line
    plt.annotate("",
                 xy=(min_, min_), xycoords='data',
                 xytext=(max_, max_), textcoords='data',
                 arrowprops=dict(arrowstyle="-", edgecolor="blue", alpha=.5, linewidth=.5,
                                 connectionstyle="arc3,rad=0."))
    plt.axis([min_, max_, min_, max_])

    plt.savefig('plot_evaluation_scatter.png')


def plot_series_one_year_for_talk(df):
    import pandas as pd
    from transnet.get_data_from_api import actual_value_mw

    df = df[[actual_value_mw]]

    logger.info(df.mean())
    df['moving avg (2 weeks)'] = pd.rolling_mean(df[actual_value_mw], window=14 * 24 * 4)
    df2 = df.loc['2017-09-18':'2017-09-24', actual_value_mw]

    df.plot(figsize=(16, 6), subplots=False)
    df2.plot(figsize=(16, 6), subplots=False)
    plt.title('One year')
    plt.savefig('plot_ts_year.png')

    plt.figure()
    df = df.loc['2017-09-18':'2017-09-24', actual_value_mw]
    df.plot(figsize=(10, 5), subplots=False)
    plt.title('One week')
    plt.savefig('plot_ts_week.png')
