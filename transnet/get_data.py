import glob
import logging
import os
from datetime import date
from enum import Enum

import pandas as pd
import requests
from dateutil.rrule import rrule, MONTHLY
from statsmodels.tsa.seasonal import seasonal_decompose

from transnet import get_data_path
from transnet.get_feiertage import get_feiertage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# see https://www.transnetbw.com/en/transparency/market-data/key-figures
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

    df = preprocess_df(df)
    return df


def preprocess_df(df):
    # parse datetime and set as index
    df['temporary'] = df[['Date from', 'Time from']].apply(lambda x: '{} {}'.format(x[0], x[1]), axis=1)
    df['date'] = pd.to_datetime(df['temporary'], format='%d.%m.%Y %H:%M', errors='ignore')
    df = df.set_index(pd.DatetimeIndex(df['date']))

    # remove rows with missing values (e.g. for Zeitumstellung on 26.10.2014)
    missing_values = df[actual_value_mw].isnull()
    df = df[-missing_values]
    # replace missing actual values by projections (occurs at 2013-05-08)
    zero_values = df[actual_value_mw] == 0
    df.loc[zero_values, actual_value_mw] = df.loc[zero_values, projection_mw]
    # restrict
    df = df[[actual_value_mw]]

    # subtract 7day rolling average
    # rolling_mean = pd.rolling_mean(df, window=30 * 24 * 4)
    # expweighted_avg = pd.ewma(df, halflife=7 * 24 * 4)
    # df['rolling_mean'] = rolling_mean
    # df['expweighted_avg'] = expweighted_avg
    # df = df['2013-01-01':]
    # df[actual_value_mw] = df[actual_value_mw] - df['one_year_rolling_avg']

    df = _groupby_date(df)

    df = _add_weekday(df)
    df = _add_holidays(df)

    # decompose T = day
    ##df_decomp_daily = _seasonal_decompose(df, freq=24 * 4)
    ##df[actual_value_mw] = df[actual_value_mw] - df_decomp_daily['trend']

    # decompose T = week
    # df_decomp_weekly = _seasonal_decompose(df, freq=7 * 24 * 4)

    ##df['daily_trend'] = df_decomp_daily['trend']
    # df['weekly_trend'] = df_decomp_weekly['trend']
    # df['weekly_seasonal'] = df_decomp_weekly['seasonal']
    # df['weekly_resid'] = df_decomp_weekly['resid']

    # df = df.loc['2017-05-01':'2017-05-31', ['resid']]

    # df.loc['2017-05-01':'2017-05-01', 'resid'] += 2000

    return df  # df[[actual_value_mw, 'rolling_mean']]


def _add_weekday(df):
    # from 0=monday to 6=sunday
    df['weekday'] = df.index.weekday * 1000
    return df


def _add_holidays(df):
    # holiday=-1
    holidays = get_feiertage()
    df['holiday_name'] = holidays
    is_holiday = ~df['holiday_name'].isnull()
    df.loc[is_holiday, 'weekday'] = -1 * 1000
    return df


def _seasonal_decompose(df, freq):
    decomposition = seasonal_decompose(df, model='additive', freq=freq, two_sided=False)
    df2 = pd.DataFrame(index=df.index)
    df2['seasonal'] = decomposition.seasonal
    df2['trend'] = decomposition.trend
    df2['resid'] = decomposition.resid
    return df2


def _groupby_date(df):
    series = df.groupby(by=lambda x: x.date())[actual_value_mw].mean()
    df = pd.DataFrame(series)
    df = df.set_index(df.index.to_datetime())
    return df
