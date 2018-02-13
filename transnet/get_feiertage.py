import logging
import os

import json

import csv

import requests
from transnet import get_data_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# see https://www.transnetbw.com/en/transparency/market-data/key-figures
api = 'https://feiertage-api.de/api'


def save_csv():
    path_for_type = get_data_path('feiertage')
    os.makedirs(path_for_type, exist_ok=True)

    feiertage_dict = {}
    years = range(2011, 2019)
    for year in years:
        logger.info('Retrieving Feiertage for BW for year {}'.format(year))

        params = {'jahr': year, 'nur_land': 'BW'}
        r = requests.get(api, params=params)
        r.raise_for_status()

        feiertage_dict_for_year = json.loads(r.text)
        feiertage_dict.update({year: feiertage_dict_for_year})

    feiertage_list = []
    for year in feiertage_dict.keys():
        for feiertag in iter(feiertage_dict[year].keys()):
            datum = feiertage_dict[year][feiertag]['datum']
            feiertage_list.append((datum, feiertag))

    file_name = 'feiertage.csv'.format(year)
    file_path = os.path.join(path_for_type, file_name)
    with open(file_path, 'w') as f:
        csv_out=csv.writer(f)
        csv_out.writerow(['date', 'name'])
        for row in feiertage_list:
            csv_out.writerow(row)