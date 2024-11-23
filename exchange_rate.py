"""
Summary.

Exchange rate extracted from Brazil central bank.
"""
# -*- coding: utf-8 -*-

from datetime import date, timedelta
import pandas as pd
import requests


def ptax_bcb(start_date, currency):
    """
    Summary.

    Function to access BCB open data API.
    start_date: String. Date in mm-dd-AAAA format.
    currency: String. currency code.
    """
    fim = (date.today()-timedelta(days=1)).strftime("%m-%d-%Y")
    moeda = currency
    df1 = pd.DataFrame({"dataCotacao": pd.date_range(start=start_date,
                                                     end=fim)})
    df1["dataCotacao"] = df1["dataCotacao"].dt.date
    df1["dataCotacao"] = df1["dataCotacao"].astype(str)
    url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/" +
           "CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial," +
           "dataFinalCotacao=@dataFinalCotacao)?" +
           "@moeda='{}'&@dataInicial='{}'&@dataFinalCotacao='{}'" +
           "&$filter=tipoBoletim%20eq%20'Fechamento'&$format=json&$select=" +
           "cotacaoCompra,cotacaoVenda,dataHoraCotacao")  # URL.
    url = url.format(moeda, start_date, fim)
    page = requests.get(url, timeout=None).json()
    df2 = pd.DataFrame(page["value"])
    # # Adjustments.
    tmp = {"cotacaoCompra": "numPTAXCompra"+currency,
           "cotacaoVenda": "numPTAXVenda"+currency,
           "dataHoraCotacao": "datahoraCotacao"}
    df2 = df2.rename(columns=tmp)  # Renaming columns.
    df2["datahoraCotacao"] = pd.to_datetime(df2["datahoraCotacao"])
    df2["dataCotacao"] = df2["datahoraCotacao"].dt.date
    df2["dataCotacao"] = df2["dataCotacao"].astype(str)
    df2["horaCotacao"] = df2["datahoraCotacao"].dt.time
    df2["horaCotacao"] = df2["horaCotacao"].astype(str)
    df = pd.merge(df1, df2, how="left", on="dataCotacao")
    df["horaCotacao"] = df["horaCotacao"].ffill()
    df["numPTAXCompra"+currency] = df["numPTAXCompra"+currency].ffill()
    df["numPTAXVenda"+currency] = df["numPTAXVenda"+currency].ffill()
    # Necessary informations.
    # df2 = df2[df2["tipoBoletim"] == "Fechamento"]
    df = df.dropna(subset="numPTAXCompra"+currency)  # Necessary rows.
    df["idtbCotacao"+currency] = df.reset_index().index + 1  # ID.
    df = df[["idtbCotacaoUSD", "dataCotacao", "horaCotacao",
             "numPTAXCompra"+currency, "numPTAXVenda"+currency]]
    return df


def ptax_today_bcb(currency):
    """
    Summary.

    Function to access BCB open data API to get current price a currency.
    currency: String. currency code.
    """
    inicio = (date.today() - timedelta(days=7)).strftime("%m-%d-%Y")
    fim = date.today().strftime("%m-%d-%Y")
    url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/" +
           "CotacaoMoedaPeriodoFechamento(codigoMoeda=@codigoMoeda," +
           "dataInicialCotacao=@dataInicialCotacao," +
           "dataFinalCotacao=@dataFinalCotacao)?@codigoMoeda='{}'" +
           "&@dataInicialCotacao='{}'&@dataFinalCotacao='{}'&$format=json" +
           "&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao")  # URL.
    url = url.format(currency, inicio, fim)
    page = requests.get(url, timeout=None).json()
    df = pd.DataFrame(page["value"])
    # # Adjustments.
    tmp = {"cotacaoCompra": "COTAÇÃO COMPRA", "cotacaoVenda": "COTAÇÃO VENDA",
           "dataHoraCotacao": "datahoraCotacao"}
    df = df.rename(columns=tmp)  # Renaming columns.
    df["datahoraCotacao"] = pd.to_datetime(df["datahoraCotacao"])
    df["DATA COTAÇÃO"] = df["datahoraCotacao"].dt.date
    df["DATA COTAÇÃO"] = df["DATA COTAÇÃO"].astype(str)
    df["HORA COTAÇÃO"] = df["datahoraCotacao"].dt.time
    df["HORA COTAÇÃO"] = df["HORA COTAÇÃO"].astype(str)
    df["MOEDA"] = currency
    df = df[["MOEDA", "DATA COTAÇÃO", "HORA COTAÇÃO",
             "COTAÇÃO COMPRA", "COTAÇÃO VENDA"]]
    df = df.T.reset_index(drop=False)
    # df = df.rename(columns={"index": "DADO", 0: "VALOR"})
    ptax = df.loc[3, 0]
    return ptax


def ptax_today(currency):
    """
    Summary.

    Function to access Awesomeapi API to get current price a currency.
    currency: String. currency code.
    """
    url = "https://economia.awesomeapi.com.br/last/{}"
    url = url.format(currency)
    page = requests.get(url, timeout=None).json()
    df = pd.DataFrame(page)
    df = df.T.reset_index(drop=False)
    df["TICKET"] = df["code"] + "-" + df["codein"]
    df["name"] = df["name"].str.upper()
    column_mapping = {"bid": "COTAÇÃO COMPRA",
                      "ask": "COTAÇÃO VENDA", "name": "NOME"}
    df = df.rename(columns=column_mapping)
    df = df[["TICKET", "NOME", "COTAÇÃO COMPRA", "COTAÇÃO VENDA"]]
    # df = (df[df["TICKET"] == currency].reset_index(drop=True))
    df = df.rename(columns={"COTAÇÃO COMPRA": "VALOR"})
    df = df[["TICKET", "VALOR"]]
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")
    # ptax = df.T.reset_index(drop=False)
    # ptax = ptax.loc[1, 0]
    return df
