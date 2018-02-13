import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

from transnet.get_data_from_api import get_df_for_type, actual_value_mw
from transnet.preprocess import preprocess_df
from transnet.correlation import get_acf

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_data():
    df = get_df_for_type()
    df = preprocess_df(df)

    logger.info(df.info())
    logger.info(df.head())

    plt.figure()
    df[[actual_value_mw, 'weekday']].plot(figsize=(13, 8), subplots=False)
    plt.savefig('plot_ts.png')

    plt.figure(figsize=(13, 8))
    lag_acf = get_acf(df[[actual_value_mw]])
    plt.plot(lag_acf)
    plt.savefig('plot_acf.png')
