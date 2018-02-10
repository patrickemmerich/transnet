from datetime import date
from os import path, makedirs

import requests
from dateutil.rrule import rrule, MONTHLY

from transnet import get_data_path

# see https://www.transnetbw.com/en/transparency/market-data/key-figures
api = 'https://api.transnetbw.de'
load = 'regulationZone'
photovoltaics_infeed = 'photovoltaics'
wind_infeed = 'wind'

# months = [day.strftime('%Y-%m') for day in rrule(MONTHLY, dtstart=date(2011, 1, 1), until=date.today())]
months = [day.strftime('%Y-%m') for day in rrule(MONTHLY, dtstart=date(2011, 1, 1), until=date(2011, 3, 1))]


def save_csv(type=load):
    path_for_type = get_data_path(type)
    makedirs(path_for_type, exist_ok=True)

    for month in months:
        params = {'language': 'en', 'date': month}
        r = requests.get('{}/{}/csv'.format(api, type), params=params)
        r.raise_for_status()
        content = r.content
        file_name = '{}.csv'.format(month)
        file_path = path.join(path_for_type, file_name)
        with open(file_path, 'wb') as f:
            f.write(content)
