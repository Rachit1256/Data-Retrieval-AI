import pandas as pd


def correlation(df):

    numeric = df.select_dtypes(include="number")

    return numeric.corr().round(2).to_dict()