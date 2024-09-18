"""
Summary.

Exchange rate extracted from Brazil central bank.
"""
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from datetime import date, timedelta


def ptax_bcb(StartDate, Currency):
    """
    Summary.

    Function to access BCB open data API.
    StartDate: String. Date in mm-dd-AAAA format.
    Currency: String. Currency code.
    """
    fim = (date.today()-timedelta(days=1)).strftime("%m-%d-%Y")
    moeda = Currency
    df1 = pd.DataFrame({"dataCotacao": pd.date_range(start=StartDate,
                                                     end=fim)})
    df1["dataCotacao"] = df1["dataCotacao"].dt.date
    df1["dataCotacao"] = df1["dataCotacao"].astype(str)
    url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/" +
           "CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial," +
           "dataFinalCotacao=@dataFinalCotacao)?" +
           "@moeda='{}'&@dataInicial='{}'&@dataFinalCotacao='{}'" +
           "&$filter=tipoBoletim%20eq%20'Fechamento'&$format=json&$select=" +
           "cotacaoCompra,cotacaoVenda,dataHoraCotacao")  # URL.
    url = url.format(moeda, StartDate, fim)
    page = requests.get(url).json()
    df2 = pd.DataFrame(page["value"])
    # # Adjustments.
    tmp = {"cotacaoCompra": "numPTAXCompra"+Currency,
           "cotacaoVenda": "numPTAXVenda"+Currency,
           "dataHoraCotacao": "datahoraCotacao"}
    df2 = df2.rename(columns=tmp)  # Renaming columns.
    df2["datahoraCotacao"] = pd.to_datetime(df2["datahoraCotacao"])
    df2["dataCotacao"] = df2["datahoraCotacao"].dt.date
    df2["dataCotacao"] = df2["dataCotacao"].astype(str)
    df2["horaCotacao"] = df2["datahoraCotacao"].dt.time
    df2["horaCotacao"] = df2["horaCotacao"].astype(str)
    df = pd.merge(df1, df2, how="left", on="dataCotacao")
    df["horaCotacao"] = df["horaCotacao"].ffill()
    df["numPTAXCompra"+Currency] = df["numPTAXCompra"+Currency].ffill()
    df["numPTAXVenda"+Currency] = df["numPTAXVenda"+Currency].ffill()
    # Necessary informations.
    # df2 = df2[df2["tipoBoletim"] == "Fechamento"]
    df = df.dropna(subset="numPTAXCompra"+Currency)  # Necessary rows.
    df["idtbCotacao"+Currency] = df.reset_index().index + 1  # ID.
    df = df[["idtbCotacaoUSD", "dataCotacao", "horaCotacao",
             "numPTAXCompra"+Currency, "numPTAXVenda"+Currency]]
    return df


def ptax_today_bcb(Currency):
    """
    Summary.

    Function to access BCB open data API to get current price a currency.
    Currency: String. Currency code.
    """
    inicio = (date.today() - timedelta(days=7)).strftime("%m-%d-%Y")
    fim = date.today().strftime("%m-%d-%Y")
    url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/" +
           "CotacaoMoedaPeriodoFechamento(codigoMoeda=@codigoMoeda," +
           "dataInicialCotacao=@dataInicialCotacao," +
           "dataFinalCotacao=@dataFinalCotacao)?@codigoMoeda='{}'" +
           "&@dataInicialCotacao='{}'&@dataFinalCotacao='{}'&$format=json" +
           "&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao")  # URL.
    url = url.format(Currency, inicio, fim)
    page = requests.get(url).json()
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
    df["MOEDA"] = Currency
    df = df[["MOEDA", "DATA COTAÇÃO", "HORA COTAÇÃO",
             "COTAÇÃO COMPRA", "COTAÇÃO VENDA"]]
    df = df.T.reset_index(drop=False)
    # df = df.rename(columns={"index": "DADO", 0: "VALOR"})
    ptax = df.loc[3, 0]
    return ptax


def ptax_today(Currency):
    """
    Summary.

    Function to access Awesomeapi API to get current price a currency.
    Currency: String. Currency code.
    """
    url = "https://economia.awesomeapi.com.br/last/{}"
    url = url.format(Currency)
    page = requests.get(url).json()
    """
    url = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL," +
                       "USD-BRLT,CAD-BRL,EUR-BRL,GBP-BRL,ARS-BRL,BTC-BRL," +
                       "LTC-BRL,JPY-BRL,CHF-BRL,AUD-BRL,CNY-BRL,ILS-BRL," +
                       "ETH-BRL,XRP-BRL,EUR-USD,CAD-USD,GBP-USD,ARS-USD," +
                       "JPY-USD,CHF-USD,AUD-USD,CNY-USD,ILS-USD,BTC-USD," +
                       "LTC-USD,ETH-USD,XRP-USD,BRL-USD,BRL-EUR,USD-EUR," +
                       "CAD-EUR,GBP-EUR,ARS-EUR,JPY-EUR,CHF-EUR,AUD-EUR," +
                       "CNY-EUR,ILS-EUR,BTC-EUR,LTC-EUR,ETH-EUR,XRP-EUR," +
                       "DOGE-BRL,DOGE-EUR,DOGE-USD,USD-JPY,USD-CHF,USD-CAD," +
                       "NZD-USD,USD-ZAR,USD-TRY,USD-MXN,USD-PLN,USD-SEK," +
                       "USD-SGD,USD-DKK,USD-NOK,USD-ILS,USD-HUF,USD-CZK," +
                       "USD-THB,USD-AED,USD-JOD,USD-KWD,USD-HKD,USD-SAR," +
                       "USD-INR,USD-KRW,FJD-USD,GHS-USD,KYD-USD,SGD-USD," +
                       "USD-ALL,USD-AMD,USD-ANG,USD-ARS,USD-AUD,USD-BBD," +
                       "USD-BDT,USD-BGN,USD-BHD,USD-BIF,USD-BND,USD-BOB," +
                       "USD-BSD,USD-BWP,USD-BZD,USD-CLP,USD-CNY,USD-COP," +
                       "USD-CRC,USD-CUP,USD-DJF,USD-DOP,USD-DZD,USD-EGP," +
                       "USD-ETB,USD-FJD,USD-GBP,USD-GEL,USD-GHS,USD-GMD," +
                       "USD-GNF,USD-GTQ,USD-HNL,USD-HRK,USD-HTG,USD-IDR," +
                       "USD-IQD,USD-IRR,USD-ISK,USD-JMD,USD-KES,USD-KHR," +
                       "USD-KMF,USD-KZT,USD-LAK,USD-LBP,USD-LKR,USD-LSL," +
                       "USD-LYD,USD-MAD,USD-MDL,USD-MGA,USD-MKD,USD-MMK," +
                       "USD-MOP,USD-MRO,USD-MUR,USD-MVR,USD-MWK,USD-MYR," +
                       "USD-NAD,USD-NGN,USD-NIO,USD-NPR,USD-NZD,USD-OMR," +
                       "USD-PAB,USD-PEN,USD-PGK,USD-PHP,USD-PKR,USD-PYG," +
                       "USD-QAR,USD-RON,USD-RSD,USD-RWF,USD-SCR,USD-SDG," +
                       "USD-SOS,USD-STD,USD-SVC,USD-SYP,USD-SZL,USD-TND," +
                       "USD-TTD,USD-TWD,USD-TZS,USD-UAH,USD-UGX,USD-UYU," +
                       "USD-UZS,USD-VEF,USD-VND,USD-VUV,USD-XAF,USD-XCD," +
                       "USD-XOF,USD-XPF,USD-YER,USD-ZMK,AED-USD,DKK-USD," +
                       "HKD-USD,MXN-USD,NOK-USD,PLN-USD,RUB-USD,SAR-USD," +
                       "SEK-USD,TRY-USD,TWD-USD,VEF-USD,ZAR-USD,UYU-USD," +
                       "PYG-USD,CLP-USD,COP-USD,PEN-USD,NIO-USD,BOB-USD," +
                       "KRW-USD,EGP-USD,USD-BYN,USD-MZN,INR-USD,JOD-USD," +
                       "KWD-USD,USD-AZN,USD-CNH,USD-KGS,USD-TJS,USD-RUB," +
                       "MYR-USD,UAH-USD,HUF-USD,IDR-USD,USD-AOA,VND-USD," +
                       "BYN-USD,XBR-USD,THB-USD,PHP-USD,USD-TMT,XAGG-USD," +
                       "USD-MNT,USD-AFN,AFN-USD,SYP-USD,IRR-USD,IQD-USD," +
                       "USD-NGNI,USD-ZWL,BRL-ARS,BRL-AUD,BRL-CAD,BRL-CHF," +
                       "BRL-CLP,BRL-DKK,BRL-HKD,BRL-JPY,BRL-MXN,BRL-SGD," +
                       "SGD-BRL,AED-BRL,BRL-AED,BRL-BBD,BRL-BHD,BRL-CNY," +
                       "BRL-CZK,BRL-EGP,BRL-GBP,BRL-HUF,BRL-IDR,BRL-ILS," +
                       "BRL-INR,BRL-ISK,BRL-JMD,BRL-JOD,BRL-KES,BRL-KRW," +
                       "BRL-LBP,BRL-LKR,BRL-MAD,BRL-MYR,BRL-NAD,BRL-NOK," +
                       "BRL-NPR,BRL-NZD,BRL-OMR,BRL-PAB,BRL-PHP,BRL-PKR," +
                       "BRL-PLN,BRL-QAR,BRL-RON,BRL-RUB,BRL-SAR,BRL-SEK," +
                       "BRL-THB,BRL-TRY,BRL-VEF,BRL-XAF,BRL-XCD,BRL-XOF," +
                       "BRL-ZAR,BRL-TWD,DKK-BRL,HKD-BRL,MXN-BRL,NOK-BRL," +
                       "NZD-BRL,PLN-BRL,SAR-BRL,SEK-BRL,THB-BRL,TRY-BRL," +
                       "TWD-BRL,VEF-BRL,ZAR-BRL,BRL-PYG,BRL-UYU,BRL-COP," +
                       "BRL-PEN,BRL-BOB,CLP-BRL,PYG-BRL,UYU-BRL,COP-BRL," +
                       "PEN-BRL,BOB-BRL,RUB-BRL,INR-BRL,EUR-GBP,EUR-JPY," +
                       "EUR-CHF,EUR-AUD,EUR-CAD,EUR-NOK,EUR-DKK,EUR-PLN," +
                       "EUR-NZD,EUR-SEK,EUR-ILS,EUR-TRY,EUR-THB,EUR-ZAR," +
                       "EUR-MXN,EUR-SGD,EUR-HUF,EUR-HKD,EUR-CZK,EUR-KRW," +
                       "BHD-EUR,EUR-AED,EUR-AFN,EUR-ALL,EUR-ANG,EUR-ARS," +
                       "EUR-BAM,EUR-BBD,EUR-BDT,EUR-BGN,EUR-BHD,EUR-BIF," +
                       "EUR-BND,EUR-BOB,EUR-BSD,EUR-BWP,EUR-BYN,EUR-BZD," +
                       "EUR-CLP,EUR-CNY,EUR-COP,EUR-CRC,EUR-CUP,EUR-CVE," +
                       "EUR-DJF,EUR-DOP,EUR-DZD,EUR-EGP,EUR-ETB,EUR-FJD," +
                       "EUR-GHS,EUR-GMD,EUR-GNF,EUR-GTQ,EUR-HNL,EUR-HRK," +
                       "EUR-HTG,EUR-IDR,EUR-INR,EUR-IQD,EUR-IRR,EUR-ISK," +
                       "EUR-JMD,EUR-JOD,EUR-KES,EUR-KHR,EUR-KWD,EUR-KYD," +
                       "EUR-KZT,EUR-LAK,EUR-LBP,EUR-LKR,EUR-LSL,EUR-LYD," +
                       "EUR-MAD,EUR-MDL,EUR-MGA,EUR-MKD,EUR-MMK,EUR-MOP," +
                       "EUR-MRO,EUR-MUR,EUR-MWK,EUR-MYR,EUR-NAD,EUR-NGN," +
                       "EUR-NIO,EUR-NPR,EUR-OMR,EUR-PAB,EUR-PEN,EUR-PGK," +
                       "EUR-PHP,EUR-PKR,EUR-PYG,EUR-QAR,EUR-RON,EUR-RSD," +
                       "EUR-RWF,EUR-SAR,EUR-SCR,EUR-SDG,EUR-SDR,EUR-SOS," +
                       "EUR-STD,EUR-SVC,EUR-SYP,EUR-SZL,EUR-TND,EUR-TTD," +
                       "EUR-TWD,EUR-TZS,EUR-UAH,EUR-UGX,EUR-UYU,EUR-UZS," +
                       "EUR-VEF,EUR-VND,EUR-XAF,EUR-XOF,EUR-XPF,EUR-ZMK," +
                       "GHS-EUR,NZD-EUR,SGD-EUR,AED-EUR,DKK-EUR,EUR-XCD," +
                       "HKD-EUR,MXN-EUR,NOK-EUR,PLN-EUR,RUB-EUR,SAR-EUR," +
                       "SEK-EUR,TRY-EUR,TWD-EUR,VEF-EUR,ZAR-EUR,MAD-EUR," +
                       "KRW-EUR,EGP-EUR,EUR-MZN,INR-EUR,JOD-EUR,KWD-EUR," +
                       "EUR-AZN,EUR-AMD,EUR-TJS,EUR-RUB,HUF-EUR,GEL-EUR," +
                       "EUR-GEL,IDR-EUR,EUR-AOA,BYN-EUR,XAGG-EUR,PEN-EUR")
    """
    df = pd.DataFrame(page)
    df = df.T.reset_index(drop=False)
    df["TICKET"] = df["code"] + "-" + df["codein"]
    df["name"] = df["name"].str.upper()
    column_mapping = {"bid": "COTAÇÃO COMPRA",
                      "ask": "COTAÇÃO VENDA", "name": "NOME"}
    df = df.rename(columns=column_mapping)
    df = df[["TICKET", "NOME", "COTAÇÃO COMPRA", "COTAÇÃO VENDA"]]
    # df = (df[df["TICKET"] == Currency].reset_index(drop=True))
    df = df.rename(columns={"COTAÇÃO COMPRA": "VALOR"})
    df = df[["TICKET", "VALOR"]]
    df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")
    # ptax = df.T.reset_index(drop=False)
    # ptax = ptax.loc[1, 0]
    return df


a = ptax_bcb(StartDate="01-01-2018", Currency="USD")
b = ptax_today_bcb(Currency="USD")
c = ptax_today(Currency="USD-BRL")
