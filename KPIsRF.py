"""
Summary.

Exchange rate function.
"""
# -*- coding: utf-8 -*-

import pandas as pd

def cdi_annually():
    """
    Summary.

    Function to access BCB open data API.
    """
    df = pd.read_json("https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/" +
                      "dados?formato=json")
    df = df.rename(columns={"data": "dataValor", "valor": "numValor"})
    df["dataValor"] = pd.to_datetime(df["dataValor"],
                                     format="%d/%m/%Y").dt.date
    df["dataValor"] = df["dataValor"].astype(str)
    df["numValor"] = df["numValor"].apply(lambda x: f"{x}%"
                                          if pd.notna(x) else x)
    df["idtbSelic"] = df.reset_index().index + 1  # ID.
    df = df[["idtbSelic", "dataValor", "numValor"]]
    return df


def cdi_annually_today():
    """
    Summary.

    Function to access BCB open data API.
    """
    df = cdi_annually()
    # cdi = (df[df["dataValor"] == df["dataValor"].max()]
    #        .reset_index(drop=True))
    cdi = df.loc[len(df)-1:, ].reset_index(drop=True)
    cdi["dataValor"] = cdi["dataValor"].astype(str)
    cdi["numValor"] = cdi["numValor"].str.replace("%", "", regex=False)
    cdi["numValor"] = pd.to_numeric(cdi["numValor"], errors="coerce")
    cdi = cdi.T.reset_index(drop=False)
    # cdi = cdi.rename(columns={"index": "DADO", 0: "VALOR"})
    cdi = cdi.loc[2, 0]
    return cdi


a = cdi_annually()
b = cdi_annually_today()
