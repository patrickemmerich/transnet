import matplotlib
import pandas as pd

matplotlib.use('agg')
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import acf, pacf

from transnet.get_data_from_api import get_df_for_type
from transnet.preprocess import preprocess_df, actual_value_mw, projection_mw
import logging
from transnet.model import get_forecast
from transnet.stat_tests import test_stationarity

from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO alternative Facebook Prophet
# https://research.fb.com/prophet-forecasting-at-scale/
# http://machinelearningstories.blogspot.de/2017/05/facebooks-phophet-model-for-forecasting.html

def plot_data():
    date_from = datetime(2017, 7, 1, 0, 0, 0)
    date_upto = datetime(2017, 7, 26, 23, 45, 0)
    horizon = timedelta(hours=2 * 24)
    horizon_quantiles = int(horizon / timedelta(minutes=15))

    df = get_df_for_type()
    df = preprocess_df(df, date_from=date_from, date_upto=date_upto)

    df[[actual_value_mw, 'seasonal', 'trend', 'residuals']].plot(figsize=(13, 8), subplots=False)
    plt.title('Timeseries')
    plt.savefig('plot_ts.png')

    # define (residuals) timeseries, which we will forecast
    timeseries = df.loc[~df['residuals'].isnull(), 'residuals']

    plt.figure(figsize=(13, 8))
    plt.title('Autocorrelation')
    lag_acf = acf(timeseries, nlags=14 * 24 * 4)
    plt.axvline(x=1 * 24 * 4, linestyle='--', color='gray')
    plt.axvline(x=7 * 24 * 4, linestyle='--', color='gray')
    # plt.axhline(y=1.96 / np.sqrt(len(df.loc[~df['residuals'].isnull(), 'residuals'])), linestyle='--', color='gray')
    plt.scatter(x=range(len(lag_acf)), y=list(lag_acf))
    plt.savefig('plot_acf.png')

    plt.figure(figsize=(13, 8))
    plt.title('Partial Autocorrelation')
    lag_pacf = pacf(timeseries, nlags=24 * 4)
    # plt.axhline(y=1.96 / np.sqrt(len(df.loc[~df['residuals'].isnull(), 'residuals'])), linestyle='--', color='gray')
    plt.scatter(x=range(len(lag_pacf)), y=list(lag_pacf))
    plt.savefig('plot_pacf.png')

    # predict
    series_starts = timeseries.index[0]
    train = timeseries.loc[series_starts: date_upto - horizon]
    holdout = df.loc[date_upto - horizon + timedelta(minutes=15): date_upto, actual_value_mw]
    test_stationarity(train)

    prediction = get_forecast(train, p=2, d=0, q=0, horizon=horizon_quantiles)
    prediction_transnet = df.loc[date_upto - horizon + timedelta(minutes=15): date_upto, projection_mw]

    seasonal_from = date_upto - timedelta(hours=7 * 24)
    seasonal = df.loc[seasonal_from + timedelta(minutes=15): seasonal_from + horizon, 'seasonal']
    seasonal.index = prediction.index
    # TODO perhaps replace by EMOV
    trend = pd.Series(data=(df.loc[(train.index[-1]), 'trend']), index=prediction.index)

    plt.figure(figsize=(13, 8))
    plt.title('Evaluation')
    plt.plot(holdout, color='blue')
    plt.plot(trend + seasonal + prediction, color='red')
    plt.plot(prediction_transnet, color='green')
    plt.savefig('plot_evaluation.png')

    from sklearn.metrics import mean_absolute_error
    logger.info('MAE holdout - forecast {}'.format(mean_absolute_error(holdout, trend + seasonal + prediction)))
    logger.info('MAE holdout - seasonal {}'.format(mean_absolute_error(holdout, trend + seasonal)))
    logger.info('MAE holdout - forecast transnet {}'.format(mean_absolute_error(holdout, prediction_transnet)))
