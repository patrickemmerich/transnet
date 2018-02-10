import matplotlib

matplotlib.use('agg')
import logging
from transnet.get_data import get_df_for_type
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_data():
    df = get_df_for_type()
    logger.info(df.info())
    logger.info(df.head())

    df.plot()
    plt.savefig('tsplot.png')
