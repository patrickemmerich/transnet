import logging
from datetime import date
from enum import Enum
from os import path, makedirs

import requests
from dateutil.rrule import rrule, MONTHLY

from transnet import get_data_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# see https://www.transnetbw.com/en/transparency/market-data/key-figures
api = 'https://api.transnetbw.de'


class Types(Enum):
    LOAD = 'regulationZone'
    PHOTOVOLTAICS_INFEED = 'photovoltaics'
    WIND_INFEED = 'wind'


def save_csv():
    for type in Types:
        save_csv_for_type(type)


def save_csv_for_type(type):
    path_for_type = get_data_path(str.lower(type.name))
    makedirs(path_for_type, exist_ok=True)

    months = [day.strftime('%Y-%m') for day in rrule(MONTHLY, dtstart=date(2011, 1, 1), until=date.today())]
    for month in months:
        logger.info('Retrieving csv for type {} and month {}'.format(type.name, month))

        params = {'language': 'en', 'date': month}
        r = requests.get('{}/{}/csv'.format(api, type.value), params=params)
        r.raise_for_status()

        file_name = '{}.csv'.format(month)
        file_path = path.join(path_for_type, file_name)
        with open(file_path, 'wb') as f:
            f.write(r.content)
