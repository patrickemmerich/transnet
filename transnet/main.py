import matplotlib
import pandas as pd

matplotlib.use('agg')

from transnet.plots import plot_acf, plot_pacf, plot_ts, plot_evaluate_ts, plot_evaluate_scatter
from transnet.get_data_from_api import get_df_for_type
from transnet.preprocess import preprocess_df, actual_value_mw, projection_mw
from transnet.model import get_forecast
from transnet.stat_tests import test_stationarity
from transnet.decompose import _seasonal_decompose
from transnet.preprocess import _add_holidays

from datetime import datetime, timedelta

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO alternative Facebook Prophet
# https://research.fb.com/prophet-forecasting-at-scale/
# http://machinelearningstories.blogspot.de/2017/05/facebooks-phophet-model-for-forecasting.html

def evaluate(
        eval_period_start=datetime(2016, 1, 1),
        eval_period_length_days=2 * 365,
        train_size=timedelta(days=2 * 30),
        n=100):
    index = pd.DatetimeIndex(
        [eval_period_start + timedelta(days=i) - timedelta(minutes=15) for i in range(eval_period_length_days)])

    df = pd.DataFrame({'date_upto': index.values}, index=index)
    df = _add_holidays(df, colname='holiday')
    df['day_after_holiday'] = df['holiday'].shift(1)
    df = df[df['holiday'].isnull() & df['day_after_holiday'].isnull()]
    df = df.sample(n, random_state=345644)
    df['date_from'] = df['date_upto'] - train_size
    df = df[['date_from', 'date_upto']]
    row_list = []
    for t in df.itertuples():
        date_from, date_upto = t[1], t[2]
        mae_prediction, mae_seasonal, mae_transnet = predict(date_from=date_from, date_upto=date_upto, plot=False)
        row_list.append((date_from, date_upto, mae_prediction, mae_seasonal, mae_transnet))

    df_eval = pd.DataFrame(row_list,
                           columns=['date_from', 'date_upto', 'mae_pred', 'mae_seasonal', 'mae_pred_transnet'])

    logger.info('EVALUATION:')
    logger.info(df_eval)
    logger.info(df_eval.mean())
    plot_evaluate_scatter(df_eval)


def predict(
        date_from=datetime(2017, 7, 1, 0, 0, 0),
        date_upto=datetime(2017, 7, 26, 23, 45, 0),
        horizon=timedelta(hours=2 * 24),
        plot=True):
    horizon_quantiles = int(horizon / timedelta(minutes=15))

    df = get_df_for_type()
    df = preprocess_df(df, date_from=date_from, date_upto=date_upto)

    train = df.loc[date_from: date_upto - horizon, actual_value_mw]
    holdout = df.loc[date_upto - horizon + timedelta(minutes=15): date_upto, actual_value_mw]
    prediction_transnet = df.loc[date_upto - horizon + timedelta(minutes=15): date_upto, projection_mw]

    df_train_decomp = _seasonal_decompose(train, freq=7 * 24 * 4)

    if plot:
        plot_ts(df_train_decomp)

    # define (residuals) timeseries, which we will forecast
    timeseries = df_train_decomp.loc[~df_train_decomp['residuals'].isnull(), 'residuals']

    if plot:
        plot_acf(timeseries)
        plot_pacf(timeseries)
        test_stationarity(timeseries)

    # predict
    prediction = get_forecast(timeseries, p=2, d=0, q=0, horizon=horizon_quantiles)

    seasonal = df_train_decomp.loc[(prediction.index - timedelta(weeks=1)), 'seasonal']
    seasonal.index = prediction.index

    # Fit of the trend seems to worsen forecast
    # historical_trend = df_train_decomp.loc[~df_train_decomp['trend'].isnull(), 'trend']
    # polynom = np.poly1d(np.polyfit(x=range(len(historical_trend)), y=historical_trend.values, deg=2))
    # trend_values = [polynom(i) for i in range(len(historical_trend), len(historical_trend) + len(prediction.index))]
    # trend = pd.Series(data=trend_values, index=prediction.index)
    trend = pd.Series(data=(df_train_decomp.loc[(train.index[-1]), 'trend']), index=prediction.index)

    df_evaluate = pd.DataFrame(index=holdout.index)
    df_evaluate['original'] = holdout
    df_evaluate['predicted'] = trend + seasonal + prediction
    df_evaluate['predicted_transnet'] = prediction_transnet
    if plot:
        plot_evaluate_ts(df_evaluate)

    from sklearn.metrics import mean_absolute_error
    mae_prediction = mean_absolute_error(holdout, trend + seasonal + prediction)
    logger.info('MAE holdout - forecast {}'.format(mae_prediction))
    mae_seasonal = mean_absolute_error(holdout, trend + seasonal)
    logger.info('MAE holdout - seasonal {}'.format(mae_seasonal))
    mae_transnet = mean_absolute_error(holdout, prediction_transnet)
    logger.info('MAE holdout - forecast transnet {}'.format(mae_transnet))

    return (mae_prediction, mae_seasonal, mae_transnet)
