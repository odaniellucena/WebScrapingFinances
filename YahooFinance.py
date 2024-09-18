"""
Summary.

Retrieve the companies infos from Yahoo Finance website.
"""
# -*- coding: utf-8 -*-

import Auxiliaries as aux
import yfinance as yf
import pandas as pd


class AllTypeAssets:
    """
    Summary.

    Retrieve the all kind of assets companies infos.
    """

    def __init__(self):
        pass

    def _parse_tables(self, ticket, country):
        if country == "BR":
            ticket = ticket.upper()
            ticket2 = ticket.upper() + ".SA"
        else:
            ticket = ticket.upper()
            ticket2 = ticket

        base = yf.Ticker(ticket2)
        dados = base.info
        if len(dados) == 1:
            raise ValueError("Page does not exist")

        if "companyOfficers" in dados:  # Removing unnecessary items.
            del dados["companyOfficers"]
        dados = pd.DataFrame([dados])
        column_mapping = {
            "beta": "BETA", "bookValue": "VALOR PATRIMONIAL/COTA",
            "country": "PAÍS", "currency": "MOEDA", "bid": "COTAÇÃO",
            "debtToEquity": "DÍVIDA BRUTA/PATRIMÔNIO", "priceToBook": "P/VP",
            "earningsGrowth": "CAGR LUCROS", "forwardPE": "P/L FUTURO",
            "earningsQuarterlyGrowth": "CAGR LUCROS TRIMESTRAL",
            "ebitda": "EBITDA", "ebitdaMargins": "MARGEM EBITDA",
            "enterpriseToEbitda": "EV/EBITDA", "overallRisk": "RISCO GERAL",
            "enterpriseToRevenue": "EV/RECEITA", "payoutRatio": "PAYOUT",
            "enterpriseValue": "VALOR DA FIRMA", "quoteType": "TIPO DE ATIVO",
            "fiftyTwoWeekHigh": "COTAÇÃO MÁXIMA USD 1 ANO",
            "fiftyTwoWeekLow": "COTAÇÃO MÍNIMA USD 1 ANO", "sector": "SETOR",
            "fiveYearAvgDividendYield": "DIVIDEND YIELD 5 ANOS",
            "forwardEps": "LPA FUTURO", "marketCap": "VALOR DE MERCADO",
            "freeCashflow": "CAIXA LIVRE", "revenuePerShare": "RECEITA/AÇÃO",
            "fullTimeEmployees": "QUANTIDADE DE FUNCIONÁRIOS",
            "grossMargins": "MARGEM BRUTA", "longName": "EMPRESA",
            "heldPercentInsiders": "PAPÉIS COM INTERNOS",
            "heldPercentInstitutions": "PAPÉIS COM INSTITUIÇÕES",
            "industry": "INDÚSTRIA", "targetMeanPrice": "COTAÇÃO ALVO",
            "netIncomeToCommon": "LUCRO LÍQUIDO", "totalRevenue": "RECEITA",
            "operatingCashflow": "CAIXA OPERACIONAL", "trailingPE": "P/L",
            "operatingMargins": "MARGEM OPERACIONAL", "category": "CATEGORIA",
            "pegRatio": "PEG RATIO", "totalCash": "TOTAL EM CAIXA",
            "profitMargins": "MARGEM DE LUCRO", "trailingEps": "LPA",
            "regularMarketVolume": "VOLUME",
            "returnOnAssets": "RETORNO SOBRE ATIVOS", "navPrice": "PREÇO/COTA",
            "returnOnEquity": "RETORNO SOBRE PATRIMÔNIO",
            "revenueGrowth": "CAGR RECEITAS TRIMESTRAL",
            "totalDebt": "DÍVIDA BRUTA", "currentRatio": "LIQUIDEZ CORRENTE",
            "sharesOutstanding": "QUANTIDADE DE PAPÉIS",
            "totalCashPerShare": "TOTAL EM CAIXA/AÇÃO", "fundFamily": "MARCA",
            "dividendYield": "DIVIDEND YIELD",
            "yield": "DIVIDEND YIELD", "totalAssets": "ATIVOS LÍQUIDOS",
            "ytdReturn": "RETORNO YTD", "beta3Year": "BETA 3 ANOS",
            "threeYearAverageReturn": "RETORNO MÉDIO 3 ANOS",
            "fiveYearAverageReturn": "RETORNO MÉDIO 5 ANOS",
            }
        dados = dados.rename(columns=column_mapping)
        cols = [coluna for coluna in dados.columns if coluna.isupper()]
        dados = dados[cols]
        dados["TICKET"] = ticket
        if "PAPÉIS COM INTERNOS" in dados.columns:
            dados["FREE FLOAT"] = (1 - (dados["PAPÉIS COM INTERNOS"] +
                                        dados["PAPÉIS COM INSTITUIÇÕES"]))
        cotacoes = base.history(start="2018-01-01", end=None)
        cotacoes.reset_index(drop=False, inplace=True)  # Reseting index.
        column_mapping = {
            "Date": "DATA", "Close": "COTAÇÃO", "Dividends": "PROVENTO PAGO"
            }
        cotacoes = cotacoes.rename(columns=column_mapping)
        cotacoes = cotacoes[["DATA", "COTAÇÃO", "PROVENTO PAGO"]]
        cotacoes["TICKET"] = ticket
        return dados, cotacoes

    def info(self, ticket, country=None):
        """
        Summary.

        Function to retrieve all kind of assets infos.
        ticket: String. Ticket code.
        country: String. "BR" ou blank.
        """
        df = self._parse_tables(ticket, country)[0]  # Dados.
        columns = ["TICKET", "PAÍS", "INDÚSTRIA", "SETOR", "EMPRESA",
                   "TIPO DE ATIVO", "QUANTIDADE DE FUNCIONÁRIOS",
                   "RISCO GERAL"]
        tmp = []

        for column in columns:
            if column in df.columns:
                tmp.append(column)
        df = df[tmp]

        tmp = ["TICKET", "PAÍS", "INDÚSTRIA", "SETOR", "EMPRESA",
               "TIPO DE ATIVO"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self, ticket, country=None):
        """
        Summary.

        Function to retrieve all kind of assets prices infos.
        ticket: String. Ticket code.
        country: String. "BR" ou blank.
        """
        df = self._parse_tables(ticket, country)[0]  # Dados.
        columns = ["TICKET", "MOEDA", "COTAÇÃO MÍNIMA USD 1 ANO", "COTAÇÃO",
                   "COTAÇÃO MÁXIMA USD 1 ANO", "COTAÇÃO ALVO"]
        tmp = []

        for column in columns:
            if column in df.columns:
                tmp.append(column)
        df = df[tmp]

        tmp = ["TICKET", "MOEDA"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self, ticket, country=None):
        """
        Summary.

        Function to retrieve all kind of assets kpi's infos.
        ticket: String. Ticket code.
        country: String. "BR" ou blank.
        """
        df = self._parse_tables(ticket, country)[0]  # Dados.
        columns = ["TICKET", "PAYOUT", "DIVIDEND YIELD 5 ANOS", "BETA", "P/L",
                   "P/L FUTURO", "VOLUME", "VALOR DE MERCADO",
                   "DIVIDEND YIELD", "VALOR DA FIRMA", "MARGEM DE LUCRO",
                   "VALOR PATRIMONIAL/COTA", "P/VP", "MARGEM BRUTA",
                   "CAGR LUCROS TRIMESTRAL", "LUCRO LÍQUIDO", "LPA",
                   "PEG RATIO", "EV/RECEITA", "EV/EBITDA", "CAIXA LIVRE",
                   "TOTAL EM CAIXA", "TOTAL EM CAIXA/AÇÃO", "EBITDA",
                   "DÍVIDA BRUTA", "RECEITA", "DÍVIDA BRUTA/PATRIMÔNIO",
                   "RETORNO SOBRE ATIVOS", "RETORNO SOBRE PATRIMÔNIO",
                   "CAIXA OPERACIONAL", "CAGR LUCROS", "LIQUIDEZ CORRENTE",
                   "CAGR RECEITAS TRIMESTRAL", "MARGEM OPERACIONAL",
                   "MARGEM EBITDA", "RECEITA/AÇÃO", "LPA FUTURO",
                   "QUANTIDADE DE PAPÉIS", "PAPÉIS COM INTERNOS", "FREE FLOAT",
                   "PAPÉIS COM INSTITUIÇÕES", "MOEDA"]
        tmp = []

        for column in columns:
            if column in df.columns:
                tmp.append(column)
        df = df[tmp]

        tmp = ["PAYOUT", "DIVIDEND YIELD", "MARGEM DE LUCRO", "MARGEM EBITDA",
               "MARGEM OPERACIONAL", "MARGEM BRUTA", "RETORNO SOBRE ATIVOS",
               "RETORNO SOBRE PATRIMÔNIO", "CAGR LUCROS TRIMESTRAL",
               "CAGR RECEITAS TRIMESTRAL", "PAPÉIS COM INTERNOS",
               "PAPÉIS COM INSTITUIÇÕES", "FREE FLOAT"]
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
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self, ticket, country=None):
        """
        Summary.

        Function to aggregate all kind of assets full infos.
        ticket: String. Ticket code.
        """
        df = pd.concat([self.info(ticket, country),
                        self.price(ticket, country),
                        self.kpi(ticket, country)])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        df = df.drop(["INFO"], axis=1)
        return df

    def payments(self, ticket, country=None):
        """
        Summary.

        Function to retrieve all kind of assets payments infos.
        ticket: String. Ticket code.
        country: String. "BR" ou blank.
        """
        df = self._parse_tables(ticket, country)[0]  # Dados.
        df = df[["MOEDA"]]
        df = self._parse_tables(ticket, country)[1]  # Pagamentos.
        df = df[df["PROVENTO PAGO"] > 0]
        df = df.reset_index(drop=True)
        df = df[["DATA", "PROVENTO PAGO", "TICKET"]]
        column_mapping = {
            "DATA": "DATA EX", "PROVENTO PAGO": "VALOR"
            }
        df = df.rename(columns=column_mapping)
        df["DATA EX"] = pd.to_datetime(df["DATA EX"]).dt.date
        df["DATA EX"] = df["DATA EX"].astype(str)
        return df


z = AllTypeAssets()

t = "wege3"
a = z.info(ticket=t, country="BR")
b = z.price(ticket=t, country="BR")
c = z.kpi(ticket=t, country="BR")
d = z.payments(ticket=t, country="BR")
e = z.table(ticket=t, country="BR")
'''
t = "visc11"
a = z.info(ticket=t, country="BR")
b = z.price(ticket=t, country="BR")
c = z.kpi(ticket=t, country="BR")
d = z.payments(ticket=t, country="BR")S
e = z.table(ticket=t, country="BR")

t = "ivvb11"
a = z.info(ticket=t, country="BR")
b = z.price(ticket=t, country="BR")
c = z.kpi(ticket=t, country="BR")
d = z.payments(ticket=t, country="BR")
e = z.table(ticket=t, country="BR")

t = "msft"
a = z.info(ticket=t)
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.payments(ticket=t)
e = z.table(ticket=t)

t = "o"
a = z.info(ticket=t)
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.payments(ticket=t)
e = z.table(ticket=t)

t = "qqq"
a = z.info(ticket=t)
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.payments(ticket=t)
e = z.table(ticket=t)
'''
