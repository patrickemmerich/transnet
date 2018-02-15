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

# see https://www.transnetbw.com/en/transparency/market-data/key-figures
api = 'https://api.transnetbw.de'
# actual_value is available until t - 30min
# predicted_value is available for t + 24h

actual_value_mw = 'Actual value (MW)'
projection_mw = 'Projection (MW)'


class Types(Enum):
    LOAD = 'regulationZone'
    PHOTOVOLTAICS_INFEED = 'photovoltaics'
    WIND_INFEED = 'wind'


def _get_path_for_type(type):
    return get_data_path(str.lower(type.name))


def save_csv():
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
    path = _get_path_for_type(type)
    filenames = glob.glob(os.path.join(path, "*.csv"))
    filenames.sort()

    # read and concatenate df's
    df_from_each_file = (pd.read_csv(f, delimiter=';') for f in filenames)
    df = pd.concat(df_from_each_file, ignore_index=True)

    return df
