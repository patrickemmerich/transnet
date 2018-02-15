import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from transnet.get_data_from_api import actual_value_mw


def _seasonal_decompose(series, freq):
    decomposition = seasonal_decompose(series, model='additive', freq=freq, two_sided=False)
    df = pd.DataFrame(index=series.index)
    df[actual_value_mw] = series
    df['seasonal'] = decomposition.seasonal
    df['trend'] = decomposition.trend
    df['residuals'] = decomposition.resid
    return df
