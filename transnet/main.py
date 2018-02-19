import matplotlib
import pandas as pd

matplotlib.use('agg')

from transnet.plots import plot_acf, plot_pacf, plot_ts, plot_evaluate
from transnet.get_data_from_api import get_df_for_type
from transnet.preprocess import preprocess_df, actual_value_mw, projection_mw
from transnet.model import get_forecast
from transnet.stat_tests import test_stationarity
from transnet.decompose import _seasonal_decompose

from datetime import datetime, timedelta

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO alternative Facebook Prophet
# https://research.fb.com/prophet-forecasting-at-scale/
# http://machinelearningstories.blogspot.de/2017/05/facebooks-phophet-model-for-forecasting.html

def predict():
    date_from = datetime(2017, 7, 1, 0, 0, 0)
    date_upto = datetime(2017, 7, 26, 23, 45, 0)
    horizon = timedelta(hours=2 * 24)
    horizon_quantiles = int(horizon / timedelta(minutes=15))

    df = get_df_for_type()
    df = preprocess_df(df, date_from=date_from, date_upto=date_upto)

    train = df.loc[date_from: date_upto - horizon, actual_value_mw]
    holdout = df.loc[date_upto - horizon + timedelta(minutes=15): date_upto, actual_value_mw]
    prediction_transnet = df.loc[date_upto - horizon + timedelta(minutes=15): date_upto, projection_mw]

    df_train_decomp = _seasonal_decompose(train, freq=7 * 24 * 4)

    plot_ts(df_train_decomp)

    # define (residuals) timeseries, which we will forecast
    timeseries = df_train_decomp.loc[~df_train_decomp['residuals'].isnull(), 'residuals']

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
    plot_evaluate(df_evaluate)

    from sklearn.metrics import mean_absolute_error
    logger.info('MAE holdout - forecast {}'.format(mean_absolute_error(holdout, trend + seasonal + prediction)))
    logger.info('MAE holdout - seasonal {}'.format(mean_absolute_error(holdout, trend + seasonal)))
    logger.info('MAE holdout - forecast transnet {}'.format(mean_absolute_error(holdout, prediction_transnet)))
