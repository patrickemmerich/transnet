import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

from transnet.get_data_from_api import get_df_for_type
from transnet.preprocess import preprocess_df, actual_value_mw
from transnet.correlation import get_acf, get_pacf
import logging
from transnet.model import get_forecast
from transnet.stat_tests import test_stationarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_data():
    df = get_df_for_type()
    df = preprocess_df(df)
    df = df['2011-08-08':'2011-08-18']

    logger.info(df.info())
    logger.info(df.head())

    df[[actual_value_mw, 'seasonal', 'trend', 'residuals']].plot(figsize=(13, 8), subplots=False)
    plt.title('Timeseries')
    plt.savefig('plot_ts.png')

    plt.figure(figsize=(13, 8))
    plt.title('Autocorrelation')
    lag_acf = get_acf(df.loc[~df['residuals'].isnull(), 'residuals'], nlags=14 * 24 * 4)
    plt.axvline(x=1 * 24 * 4, linestyle='--', color='gray')
    plt.axvline(x=7 * 24 * 4, linestyle='--', color='gray')
    # plt.axhline(y=1.96 / np.sqrt(len(df.loc[~df['residuals'].isnull(), 'residuals'])), linestyle='--', color='gray')
    plt.scatter(x=range(len(lag_acf)), y=list(lag_acf))
    plt.savefig('plot_acf.png')

    plt.figure(figsize=(13, 8))
    plt.title('Partial Autocorrelation')
    lag_pacf = get_pacf(df.loc[~df['residuals'].isnull(), 'residuals'], nlags=24 * 4)
    # plt.axhline(y=1.96 / np.sqrt(len(df.loc[~df['residuals'].isnull(), 'residuals'])), linestyle='--', color='gray')
    plt.scatter(x=range(len(lag_pacf)), y=list(lag_pacf))
    plt.savefig('plot_pacf.png')

    series_ = df.loc[~df['residuals'].isnull(), 'residuals']
    train, test = series_.loc['2011-08-08':'2011-08-17'], series_.loc['2011-08-18']
    test_stationarity(train)

    prediction = get_forecast(train, p=2, d=0, q=0, horizon=24 * 4)

    plt.figure(figsize=(13, 8))
    plt.title('Evaluation')
    plt.plot(series_.loc['2011-08-17':'2011-08-18'], color='blue')
    plt.plot(prediction, color='red')
    plt.savefig('plot_evaluation.png')
