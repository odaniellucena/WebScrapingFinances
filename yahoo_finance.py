"""
Summary.

Retrieve the companies infos from Yahoo Finance website.
"""
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

import yfinance as yf
import pandas as pd
import numpy as np


# # Common functions.
def _string_columns(df, columns):
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


def _numeric_columns(df, columns):
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


class AllTypeAssets():
    """
    Summary.

    Retrieve the all kind of assets companies infos.
    """

    def __init__(self, ticket, country):
        if country == "BR":
            self.ticket = ticket.upper()
            self.ticket2 = ticket.upper() + ".SA"
        else:
            self.ticket = ticket.upper()
            self.ticket2 = ticket

        self.base = yf.Ticker(self.ticket2)

    def _parse_data(self):
        dados = self.base.info
        if len(dados) <= 15:
            raise ValueError("Asset does not exist.")

        if "companyOfficers" in dados:  # Removing unnecessary items.
            del dados["companyOfficers"]
        dados = pd.DataFrame([dados])

        if "bid" in dados.columns:
            dados["COTAÇÃO"] = dados["bid"]
        elif "currentPrice" in dados.columns:
            dados["COTAÇÃO"] = dados["currentPrice"]
        else:
            dados["COTAÇÃO"] = np.nan

        column_mapping = {
            "beta": "BETA", "bookValue": "VALOR PATRIMONIAL/COTA",
            "country": "PAÍS", "currency": "MOEDA",
            "debtToEquity": "DÍVIDA BRUTA/PATRIMÔNIO", "priceToBook": "P/VP",
            "earningsGrowth": "CAGR LUCROS", "forwardPE": "P/L FUTURO",
            "earningsQuarterlyGrowth": "CAGR LUCROS TRIMESTRAL",
            "ebitda": "EBITDA", "ebitdaMargins": "MARGEM EBITDA",
            "enterpriseToEbitda": "EV/EBITDA", "overallRisk": "RISCO GERAL",
            "enterpriseToRevenue": "EV/RECEITA", "payoutRatio": "PAYOUT",
            "enterpriseValue": "VALOR DE FIRMA", "quoteType": "TIPO ATIVO",
            "fiftyTwoWeekHigh": "COTAÇÃO MÁXIMA 1 ANO",
            "fiftyTwoWeekLow": "COTAÇÃO MÍNIMA 1 ANO", "sectorDisp": "SETOR",
            "fiveYearAvgDividendYield": "DIVIDEND YIELD 5 ANOS",
            "forwardEps": "LPA FUTURO", "marketCap": "VALOR DE MERCADO",
            "freeCashflow": "CAIXA LIVRE", "revenuePerShare": "RECEITA/AÇÃO",
            "fullTimeEmployees": "QUANTIDADE DE FUNCIONÁRIOS",
            "grossMargins": "MARGEM BRUTA", "longName": "EMPRESA",
            "heldPercentInsiders": "PAPÉIS COM INTERNOS",
            "heldPercentInstitutions": "PAPÉIS COM INSTITUIÇÕES",
            "industryDisp": "SUBSETOR", "targetMeanPrice": "COTAÇÃO ALVO",
            "netIncomeToCommon": "LUCRO LÍQUIDO", "totalRevenue": "RECEITA",
            "operatingCashflow": "CAIXA OPERACIONAL", "trailingPE": "P/L",
            "operatingMargins": "MARGEM OPERACIONAL", "category": "CATEGORIA",
            "pegRatio": "PEG RATIO", "totalCash": "TOTAL EM CAIXA",
            "profitMargins": "MARGEM LÍQUIDA", "trailingEps": "LPA",
            "volume": "LIQUIDEZ", "legalType": "TIPO ATIVO 2",
            "returnOnAssets": "RETORNO SOBRE ATIVOS", "fundFamily": "FAMÍLIA",
            "returnOnEquity": "RETORNO SOBRE PATRIMÔNIO",
            "revenueGrowth": "CAGR RECEITAS TRIMESTRAL",
            "totalDebt": "DÍVIDA BRUTA", "currentRatio": "LIQUIDEZ CORRENTE",
            "sharesOutstanding": "QUANTIDADE DE PAPÉIS",
            "totalCashPerShare": "TOTAL EM CAIXA/AÇÃO",
            "trailingAnnualDividendYield": "DIVIDEND YIELD",
            "totalAssets": "ATIVOS LÍQUIDOS",
            "ytdReturn": "RETORNO TOTAL ACUMULADO", "beta3Year": "BETA 3 ANOS",
            "threeYearAverageReturn": "RETORNO MÉDIO 3 ANOS",
            "fiveYearAverageReturn": "RETORNO MÉDIO 5 ANOS",
            "recommendationKey": "RECOMENDAÇÃO",  # "yield": "DIVIDEND YIELD",
            "averageVolume": "LIQUIDEZ ESTIMADA",
            "fundInceptionDate": "DATA DE CRIAÇÃO",
            "navPrice": "PATRIMÔNIO LÍQUIDO/QUANTIDADE DE PAPÉIS"}
        dados = dados.rename(columns=column_mapping)
        cols = [coluna for coluna in dados.columns if coluna.isupper()]
        dados = dados[cols]
        if len(dados.columns) == 1:
            raise ValueError("Asset does not exist.")

        dados["TICKET"] = self.ticket
        return dados

    def info(self):
        """
        Summary.

        Function to retrieve the brazilian stocks infos.
        """
        df = self._parse_data()  # Dados.
        tmp = ["TICKET", "TIPO ATIVO", "EMPRESA", "PAÍS", "FAMÍLIA",
               "DATA DE CRIAÇÃO", "SETOR", "SUBSETOR", "CATEGORIA",
               "RECOMENDAÇÃO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        if "DATA DE CRIAÇÃO" in df.columns:
            df["DATA DE CRIAÇÃO"] = pd.to_datetime(
                df["DATA DE CRIAÇÃO"], unit="s").dt.date
            df["DATA DE CRIAÇÃO"] = df["DATA DE CRIAÇÃO"].astype(str)

        df = _string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the brazilian stocks prices infos.
        """
        df = self._parse_data()  # Dados.

        tmp = ["TICKET", "MOEDA", "COTAÇÃO", "COTAÇÃO ALVO",
               "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA"]
        df = _string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self):
        """
        Summary.

        Function to retrieve the brazilian stocks kpi's infos.
        """
        df = self._parse_data()  # Dados.

        if ("PAPÉIS COM INTERNOS" in df.columns or
           "PAPÉIS COM INTERNOS" in df.columns):
            df["FREE FLOAT"] = 1 - (df.get("PAPÉIS COM INTERNOS", 0) +
                                    df.get("PAPÉIS COM INSTITUIÇÕES", 0))

        tmp = ["TICKET", "MOEDA", "P/L", "P/L FUTURO", "P/VP", "EV/EBITDA",
               "EV/RECEITA", "PEG RATIO", "MARGEM EBITDA", "MARGEM BRUTA",
               "MARGEM OPERACIONAL", "MARGEM LÍQUIDA", "RETORNO SOBRE ATIVOS",
               "RETORNO SOBRE PATRIMÔNIO", "CAGR LUCROS",
               "CAGR LUCROS TRIMESTRAL", "CAGR RECEITAS TRIMESTRAL",
               "DÍVIDA BRUTA/PATRIMÔNIO", "DÍVIDA BRUTA", "LIQUIDEZ CORRENTE",
               "CAIXA LIVRE", "TOTAL EM CAIXA", "DIVIDEND YIELD",
               "DIVIDEND YIELD 5 ANOS", "PAYOUT", "BETA", "BETA 3 ANOS",
               "RISCO GERAL", "VALOR DE FIRMA", "VALOR DE MERCADO",
               "PATRIMÔNIO LÍQUIDO/QUANTIDADE DE PAPÉIS",
               "QUANTIDADE DE FUNCIONÁRIOS",
               "QUANTIDADE DE PAPÉIS", "PAPÉIS COM INTERNOS",
               "PAPÉIS COM INSTITUIÇÕES", "FREE FLOAT", "LIQUIDEZ",
               "LIQUIDEZ ESTIMADA", "RETORNO TOTAL ACUMULADO",
               "RETORNO MÉDIO 3 ANOS", "RETORNO MÉDIO 5 ANOS", "LPA",
               "VALOR PATRIMONIAL/COTA", "LPA FUTURO", "RECEITA",
               "RECEITA/AÇÃO", "CAIXA OPERACIONAL", "ATIVOS LÍQUIDOS",
               "TOTAL EM CAIXA/AÇÃO", "EBITDA"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["PAYOUT", "DIVIDEND YIELD", "MARGEM LÍQUIDA", "MARGEM EBITDA",
               "MARGEM OPERACIONAL", "MARGEM BRUTA", "RETORNO SOBRE ATIVOS",
               "RETORNO SOBRE PATRIMÔNIO", "CAGR LUCROS TRIMESTRAL",
               "CAGR RECEITAS TRIMESTRAL", "PAPÉIS COM INTERNOS",
               "PAPÉIS COM INSTITUIÇÕES", "FREE FLOAT", "CAGR LUCROS",
               "RETORNO TOTAL ACUMULADO", "RETORNO MÉDIO 3 ANOS",
               "RETORNO MÉDIO 5 ANOS"]
        for column in tmp:
            if column in df.columns:
                df[column] = df[column]*100
                df[column] = round(df[column], 2)
                df[column] = df[column].astype(str)
                df[column] = df[column].apply(lambda x: f"{x}%"
                                              if pd.notna(x) else x)

        tmp = ["DIVIDEND YIELD 5 ANOS", "DÍVIDA BRUTA/PATRIMÔNIO"]
        for column in tmp:
            if column in df.columns:
                df[column] = round(df[column], 2)
                df[column] = df[column].astype(str)
                df[column] = df[column].apply(lambda x: f"{x}%"
                                              if pd.notna(x) else x)

        tmp = ["TICKET", "MOEDA"]
        df = _string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self):
        """
        Summary.

        Function to aggregate the brazilian stocks full infos.
        """
        df = pd.concat([self.info(), self.price(), self.kpi()])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        df = df.drop(["INFO"], axis=1)

        tmp = ["P/L", "P/L FUTURO", "P/VP", "EV/EBITDA", "COTAÇÃO ALVO",
               "EV/RECEITA", "PEG RATIO", "DÍVIDA BRUTA", "LIQUIDEZ CORRENTE",
               "CAIXA LIVRE", "TOTAL EM CAIXA", "BETA", "BETA 3 ANOS",
               "RISCO GERAL", "VALOR DE FIRMA", "VALOR DE MERCADO",
               "PATRIMÔNIO LÍQUIDO/QUANTIDADE DE PAPÉIS", "RECEITA",
               "QUANTIDADE DE FUNCIONÁRIOS", "COTAÇÃO MÁXIMA 1 ANO",
               "QUANTIDADE DE PAPÉIS", "LIQUIDEZ", "LPA", "LPA FUTURO",
               "ATIVOS LÍQUIDOS", "TOTAL EM CAIXA/AÇÃO", "EBITDA",
               "VALOR PATRIMONIAL/COTA", "COTAÇÃO", "RECEITA/AÇÃO",
               "COTAÇÃO MÍNIMA 1 ANO", "CAIXA OPERACIONAL",
               "LIQUIDEZ ESTIMADA"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["PAYOUT", "DIVIDEND YIELD", "MARGEM LÍQUIDA", "MARGEM EBITDA",
               "MARGEM OPERACIONAL", "MARGEM BRUTA", "RETORNO SOBRE ATIVOS",
               "RETORNO SOBRE PATRIMÔNIO", "CAGR LUCROS TRIMESTRAL",
               "CAGR RECEITAS TRIMESTRAL", "PAPÉIS COM INTERNOS",
               "PAPÉIS COM INSTITUIÇÕES", "FREE FLOAT", "CAGR LUCROS",
               "RETORNO TOTAL ACUMULADO", "RETORNO MÉDIO 3 ANOS",
               "RETORNO MÉDIO 5 ANOS", "DIVIDEND YIELD 5 ANOS",
               "DÍVIDA BRUTA/PATRIMÔNIO"]
        for column in tmp:
            if column in df.columns:
                df[column] = df[column].str.replace("%", "", regex=False)
                df[column] = pd.to_numeric(df[column], errors="coerce")
        return df

    def payments(self, start):
        """
        Summary.

        Function to retrieve the brazilian stocks payments infos.
        """
        df = self.base.history(start=start, end=None)
        if "Dividends" not in df.columns:
            raise ValueError("Asset does not exist.")

        df.reset_index(drop=False, inplace=True)  # Reseting index.
        column_mapping = {
            "Date": "DATA", "Close": "COTAÇÃO", "Dividends": "PROVENTO PAGO"
            }
        df = df.rename(columns=column_mapping)
        df = df[["DATA", "COTAÇÃO", "PROVENTO PAGO"]]
        df["TICKET"] = self.ticket
        df = df[df["PROVENTO PAGO"] > 0]
        if len(df) == 0:
            raise ValueError("No payments.")

        df = df.reset_index(drop=True)
        df = df[["TICKET", "DATA", "PROVENTO PAGO"]]
        column_mapping = {"DATA": "DATA EX", "PROVENTO PAGO": "VALOR"}
        df = df.rename(columns=column_mapping)
        df["DATA EX"] = pd.to_datetime(df["DATA EX"]).dt.date
        df["DATA EX"] = df["DATA EX"].astype(str)
        return df
