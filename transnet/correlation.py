from statsmodels.tsa.stattools import acf, pacf


def get_acf(df):
    lag_acf = acf(df, nlags=14 * 24 * 4)
    return lag_acf


def get_pacf(df):
    lag_pacf = pacf(df, nlags=14 * 24 * 4)
    return lag_pacf
