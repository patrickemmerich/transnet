from statsmodels.tsa.stattools import acf, pacf


def get_acf(df, nlags):
    lag_acf = acf(df, nlags=nlags)
    return lag_acf


def get_pacf(df, nlags):
    lag_pacf = pacf(df, nlags=nlags)
    return lag_pacf
