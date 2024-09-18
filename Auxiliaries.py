"""
Summary.

Auxiliaries functions.
"""
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


# # Common functions.
def clean_cards(df):
    """
    Summary.

    Clean parsed cards.
    df: Dataframe.
    """
    df = df.dropna(subset=["INFO"])
    df.loc[:, "INFO"] = df["INFO"].str.replace(" / ", "/")
    df.loc[:, "INFO"] = df["INFO"].str.replace(r"^DIVIDEND YIELD.*$",
                                               "DIVIDEND YIELD", regex=True)
    df.loc[:, "INFO"] = df["INFO"].str.replace(r"^DY CAGR\(3 ANOS\).*$",
                                               "CAGR DIVIDEND YIELD 3 ANOS",
                                               regex=True)
    df.loc[:, "INFO"] = df["INFO"].str.replace(r"^VALOR CAGR\(3 ANOS\).*$",
                                               "CAGR 3 ANOS", regex=True)
    df.loc[:, "INFO"] = df["INFO"].str.replace(r"^Nº TOTAL DE PAPÉIS.*$",
                                               "QUANTIDADE DE PAPÉIS",
                                               regex=True)

    df = df[df["VALOR"] != ""]
    df["VALOR"] = df["VALOR"].str.replace("ARROW_DOWNWARD", "")
    df["VALOR"] = df["VALOR"].str.replace("ARROW_UPWARD", "")
    df.reset_index(drop=True, inplace=True)  # Reseting index.
    return df


def string_columns(df, columns):
    """
    Summary.

    Format string columns.
    df: Dataframe.
    columns: Dataframe columns.
    """
    for column in columns:
        if column in df.columns:
            df[column] = (df[column].str.replace(" %", "%", regex=False)
                          .str.replace(",", ".", regex=False)
                          .str.replace(" / ", "/", regex=False)
                          .replace({"-%": None, "-% A.A": None, "-": None,
                                    "--": None, "": None, "0.00%": None}))
            df[column] = df[column].str.upper()
    return df


def numeric_columns(df, columns):
    """
    Summary.

    Format numeric columns.
    df: Dataframe.
    columns: Dataframe columns.
    """
    for column in columns:
        if column in df.columns:
            df[column] = (df[column].str.replace("R$ ", "", regex=False)
                          .str.replace("R$\n", "", regex=False)
                          .str.replace("US$", "", regex=False)
                          .str.replace("US$\n", "", regex=False)
                          .str.replace("$ ", "", regex=False)
                          .str.replace(".", "", regex=False)
                          .str.replace(",", ".", regex=False)
                          .replace({"0": None, "0.00": None, "-": None,
                                    "--": None, "": None, np.nan: None}))
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def times(value):
    """
    Summary.

    Convert financial values ​​in words into numbers.
    value: String. String number to convert.
    """
    if value is None or value is np.nan:
        pass
    elif "MILHÃO" in value:
        return round(float(value.replace(" MILHÃO", ""))*1000000, 2)
    elif "MILHÕES" in value:
        return round(float(value.replace(" MILHÕES", ""))*1000000, 2)
    elif "MIL" in value:
        return round(float(value.replace(" MIL", ""))*1000, 2)
    elif "BILHÃO" in value:
        return round(float(value.replace(" BILHÃO", ""))*1000000000, 2)
    elif "BILHÕES" in value:
        return round(
            float(value.replace(" BILHÕES", ""))*1000000000, 2)
    elif "TRILHÃO" in value:
        return round(
            float(value.replace(" TRILHÃO", ""))*1000000000000, 2)
    elif "TRILHÕES" in value:
        return round(
            float(value.replace(" TRILHÕES", ""))*1000000000000, 2)
    else:
        return round(float(value), 2)


def times2(value):
    """
    Summary.

    Convert financial values ​​in words into numbers.
    value: String. String number to convert.
    """
    if value is None or value is np.nan:
        value = value.replace(",", ".")
        pass
    elif "K" in value:
        value = value.replace(",", ".")
        return round(float(value.replace(" K", "")) * 1000, 2)
    elif "M" in value:
        value = value.replace(",", ".")
        return round(float(value.replace(" M", "")) * 1000000, 2)
    elif "B" in value:
        value = value.replace(",", ".")
        return round(float(value.replace(" B", "")) * 1000000000, 2)
    elif "T" in value:
        value = value.replace(",", ".")
        return round(float(value.replace(" T", "")) * 1000000000000, 2)
    else:
        value = value.replace(",", ".")
        return round(float(value), 2)


def assets_out(type_asset, site):
    """
    Summary.

    Get the list of assets who is not present on the website.
    type_asset: String. Asset type.
    site: String. Site name.
    """
    df = pd.read_excel("FONTES/BASES.xlsx", sheet_name="FORA " + site)
    df = df[[type_asset]]
    df = df.dropna()
    df = set(df[type_asset])
    return df
