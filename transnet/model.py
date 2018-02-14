import logging

import pandas as pd
from statsmodels.tsa.arima_model import ARIMA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import numpy as np


def get_forecast(df, p, d, q, horizon):
    logger.info("p={}, d={}, q={}".format(p, d, q))

    model = ARIMA(df, (p, d, q))
    results = model.fit()
    forecast, stderr, conf_int = results.forecast(steps=horizon)

    array = df.index.values[-horizon:] + horizon * np.timedelta64(15, 'm')
    index = pd.DatetimeIndex(array)

    series = pd.Series(forecast, index=index)
    return series
