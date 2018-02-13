import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from transnet.get_data_from_api import actual_value_mw, projection_mw
from transnet.get_feiertage_from_api import get_holidays

actual_value_seasonal_daily_corr = 'Actual value (MW), seasonal daily corr'


def preprocess_df(df):
    df = _add_datetime_index(df)
    df = _impute_missing_values(df)
    df = df[[actual_value_mw]]

    # TODO: Apply holiday correction

    # decompose T = day
    df_decomp_daily = _seasonal_decompose(df, freq=24 * 4)
    df['seasonal_daily'] = df_decomp_daily['seasonal']
    df[actual_value_seasonal_daily_corr] = df[actual_value_mw] - df['seasonal_daily']

    df = _add_weekday(df, colname='weekday')
    df = _add_holidays(df, colnames=['weekday', 'description'])

    return df


def _add_datetime_index(df):
    df['temporary'] = df[['Date from', 'Time from']].apply(lambda x: '{} {}'.format(x[0], x[1]), axis=1)
    df['date'] = pd.to_datetime(df['temporary'], format='%d.%m.%Y %H:%M', errors='ignore')
    df = df.set_index(pd.DatetimeIndex(df['date']))
    return df


def _impute_missing_values(df):
    # remove rows with missing values (e.g. for Zeitumstellung on 26.10.2014)
    missing_values = df[actual_value_mw].isnull()
    df = df[-missing_values]
    # replace zero actual values by projections (occurs at 2013-05-08)
    zero_values = df[actual_value_mw] == 0
    df.loc[zero_values, actual_value_mw] = df.loc[zero_values, projection_mw]
    return df


def _add_weekday(df, colname='weekday'):
    # from 0=monday to 6=sunday
    df[colname] = df.index.weekday * 1000
    return df


def _add_holidays(df, colnames=['weekday', 'desciption']):
    # 7=holiday
    df_holidays = get_holidays(colname='description')

    # join, note hack to preserve index when joining
    df['date'] = df.index.date
    df_holidays['date'] = df_holidays.index.date
    df = df.merge(df_holidays, on=['date'], how='left').set_index(df.index)
    df = df.drop('date', 1)

    # overwrite weekday
    is_holiday = ~df['description'].isnull()
    df.loc[is_holiday, 'weekday'] = 7 * 1000
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
