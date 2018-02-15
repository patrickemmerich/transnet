import glob
import logging
import os
from datetime import date
from enum import Enum

import pandas as pd
import requests
from dateutil.rrule import rrule, MONTHLY

from transnet import get_data_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = 'https://api.transnetbw.de'

actual_value_mw = 'Actual value (MW)'
projection_mw = 'Projection (MW)'


class Types(Enum):
    LOAD = 'regulationZone'
    PHOTOVOLTAICS_INFEED = 'photovoltaics'
    WIND_INFEED = 'wind'


def _get_path_for_type(type):
    return get_data_path(str.lower(type.name))


def save_csv():
    """Retrieve data from Transnet API https://api.transnetbw.de. Fetch available data for total load,
    photovoltaics infeed, wind infeed (from 2011-01 until today). Resolution is 15 minutes. Data contains
    'Actual value (MW)' (up to t-30min) and 'Projection (MW)' (up to t + 24h) values where t is time of
    retrieval. Save data on monthly  basis as csv files.

    See https://www.transnetbw.com/en/transparency/market-data/key-figures on available data on the API.

    :return: None
    """
    for type in Types:
        _save_csv_for_type(type)


def _save_csv_for_type(type):
    path_for_type = _get_path_for_type(type)
    os.makedirs(path_for_type, exist_ok=True)

    months = [day.strftime('%Y-%m') for day in rrule(MONTHLY, dtstart=date(2011, 1, 1), until=date.today())]
    for month in months:
        logger.info('Retrieving csv for type {} and month {}'.format(type.name, month))

        params = {'language': 'en', 'date': month}
        r = requests.get('{}/{}/csv'.format(api, type.value), params=params)
        r.raise_for_status()

        file_name = '{}.csv'.format(month)
        file_path = os.path.join(path_for_type, file_name)
        with open(file_path, 'wb') as f:
            f.write(r.content)


def get_df_for_type(type=Types.LOAD):
    """Combine all available data (that has been retrieved from API before) for respective type, and return respective
    dataframe. Columns are 'Date from', 'Time from', 'Date to', 'Time to', 'Projection (MW)', 'Actual Value (MW)'.

    :param type:
    :return: pd.Dataframe
    """
    path = _get_path_for_type(type)
    filenames = glob.glob(os.path.join(path, "*.csv"))
    filenames.sort()

    # read and concatenate df's
    df_from_each_file = (pd.read_csv(f, delimiter=';') for f in filenames)
    df = pd.concat(df_from_each_file, ignore_index=True)

    return df
