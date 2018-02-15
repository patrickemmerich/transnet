import csv
import json
import logging
import os

import pandas as pd
import requests

from transnet import get_data_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = 'https://feiertage-api.de/api'

path_for_type = get_data_path('feiertage')
file_name = 'feiertage.csv'
file_path = os.path.join(path_for_type, file_name)


def save_csv(years=range(2011, 2019)):
    """Retrieve Baden-Wuerttemberg holidays from Feiertage API https://feiertage-api.de/api. Save data as a single
    csv file, which contains date (YYYY-MM-DD) and name (e.g. Neujahrstag) of holidays.

    :return: None"""
    os.makedirs(path_for_type, exist_ok=True)

    feiertage_dict = {}
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
            # Gründonnerstag ist kein Feiertag
            if feiertag != 'Gründonnerstag':
                datum = feiertage_dict[year][feiertag]['datum']
                feiertage_list.append((datum, feiertag))

    with open(file_path, 'w') as f:
        csv_out = csv.writer(f)
        csv_out.writerow(['date', 'name'])
        for row in feiertage_list:
            csv_out.writerow(row)


def get_holidays(colname):
    """Read holiday data (that has been retrieved from API before) from csv, and return respective
    dataframe, which has a pd.DateTimeIndex and a single column with label colname.

    :param colname:
    :return: pd.Dataframe
    """
    df = pd.read_csv(file_path, delimiter=',', parse_dates=['date'])
    df = df.set_index(pd.DatetimeIndex(df['date']))
    df.rename(columns={'name': colname}, inplace=True)
    df = df[[colname]]
    return df
