"""
Summary.

Retrieve the companies infos from Investidor 10 website.
"""
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals

from bs4 import BeautifulSoup
from lxml import etree
import requests
import pandas as pd
import numpy as np

# Header to use to get the web page content in text format.
# The User-Agent request header contains a characteristic string that allows
# the network protocol peers to identify the application type, operating
# system, software vendor or software version of the requesting software user
# agent.
# Validating User-Agent header on server side is a common operation so be sure
# to use valid browser’s User-Agent string to avoid getting blocked.
# Font: https://go-colly.org/articles/scraping_related_http_headers/
# Font: https://stackoverflow.com/questions/68259148/getting-404-error-for-
#       certain-stocks-and-pages-on-yahoo-finance-python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
    "AppleWebKit/537.36 (KHTML, like Gecko)" +
    "Chrome/71.0.3578.98 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application" +
    "/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",  # Do not track request header.
    "Connection": "close"
}


# # Common functions.
def _clean_cards(df):
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


def _times(value):
    """
    Summary.

    Convert financial values in words into numbers.
    value: String. String number to convert.
    """
    if value is None or value is np.nan:
        return None

    consts = {
        "MILHÃO": 1_000_000,
        "MILHÕES": 1_000_000,
        "MIL": 1_000,
        "BILHÃO": 1_000_000_000,
        "BILHÕES": 1_000_000_000,
        "TRILHÃO": 1_000_000_000_000,
        "TRILHÕES": 1_000_000_000_000
    }

    for k, const in consts.items():
        if k in value:
            return round(float(value.replace(f" {k}", "").strip()) * const, 2)
    return round(float(value), 2)


def _times2(value):
    """
    Summary.

    Convert financial values in words into numbers.
    value: String. String number to convert.
    """
    if value is None or value is np.nan:
        return None

    # Replace commas with dots for float conversion.
    value = value.replace(",", ".")

    consts = {
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000,
        "T": 1_000_000_000_000
    }

    for k, const in consts.items():
        if k in value:
            return round(float(value.replace(f" {k}", "").strip()) * const, 2)
    return round(float(value), 2)


def etfbr_auxtable():
    """
    Summary.

    Retrieve the auxiliar table for brazilian ETFs.
    """
    url_format = ("https://investidor10.com.br/etfs/?order=ticker&" +
                  "dir=asc&page={}")  # URL.
    df = []  # Definitive list.
    for page in range(1, 6):  # 5 pages.
        url = url_format.format(page)
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        if page.status_code != 200:
            continue
            # raise ValueError("Page does not exist")

        table = soup.find("table")  # Getting elements from tables.
        if table:
            tmp = []
            for row in table.tbody.find_all("tr"):
                column = row.find_all("td")
                if column:
                    nome = column[0].text.strip().upper()
                    ativo = column[1].text.strip().upper()
                    cotacao = column[2].text.strip().upper()
                    volume = column[3].text.strip().upper()
                    var_30d = column[4].text.strip().upper()
                    var_12m = column[5].text.strip().upper()
                    tmp.append({"NOME": nome, "ATIVO": ativo,
                                "COTAÇÃO": cotacao, "LIQUIDEZ": volume,
                                "VARIAÇÃO DE COTAÇÃO 1 MÊS": var_30d,
                                "VARIAÇÃO DE COTAÇÃO 1 ANO": var_12m})
            df.append(pd.DataFrame(tmp))

    df = pd.concat(df, ignore_index=True)  # Definitive dataframe.

    tmp = ["COTAÇÃO", "LIQUIDEZ"]
    for column in tmp:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    tmp = ["VARIAÇÃO DE COTAÇÃO 1 MÊS", "VARIAÇÃO DE COTAÇÃO 1 ANO"]
    for column in tmp:
        if column in df.columns:
            df[column] = df[column].replace({"-": None, "": None, "0": None})
            df[column] = pd.to_numeric(df[column], errors="coerce")
            df[column] = round(df[column], 2)
            df[column] = df[column].apply(lambda x: f"{x}%"
                                          if pd.notna(x) else x)

    tmp = ["NOME", "ATIVO"]
    df = _string_columns(df=df, columns=tmp)
    df.to_parquet("INVESTIDOR-10_ETFS-BR_AUX.parquet")
    return df


def etf_auxtable():
    """
    Summary.

    Retrieve the auxiliar table for ETFs.
    """
    url_format = ("https://investidor10.com.br/etfs-global/?" +
                  "order=ticker&dir=asc&page={}")  # URL.
    df = []  # Definitive list.
    for page in range(1, 106):  # 105 pages.
        url = url_format.format(page)
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        # Checking if page exist.
        if page.status_code != 200:
            continue
            # raise ValueError("Page does not exist")

        table = soup.find("table")  # # Getting elements from tables.
        if table:
            tmp = []
            for row in table.tbody.find_all("tr"):
                column = row.find_all("td")
                if column:
                    nome = column[0].text.strip().upper()
                    ativo = column[1].text.strip().upper()
                    cotacao_usd = column[2].text.strip().upper()
                    cotacao_brl = column[3].text.strip().upper()
                    # val_mercado = column[4].text.strip().upper()
                    volume_usd = column[5].text.strip().upper()
                    var_30d = column[6].text.strip().upper()
                    var_12m = column[7].text.strip().upper()
                    tmp.append({"NOME": nome, "ATIVO": ativo,
                                "VARIAÇÃO DE COTAÇÃO USD 1 ANO": var_12m,
                                "COTAÇÃO USD": cotacao_usd,
                                "COTAÇÃO BRL": cotacao_brl,
                                # "VALOR DE MERCADO USD": val_mercado,
                                "LIQUIDEZ USD": volume_usd,
                                "VARIAÇÃO DE COTAÇÃO USD 1 MÊS": var_30d})
            df.append(pd.DataFrame(tmp))

    df = pd.concat(df, ignore_index=True)  # Definitive dataframe.

    tmp = ["COTAÇÃO USD", "COTAÇÃO BRL", "VALOR DE MERCADO USD",
           "LIQUIDEZ USD"]
    for column in tmp:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    tmp = ["VARIAÇÃO DE COTAÇÃO USD 1 MÊS", "VARIAÇÃO DE COTAÇÃO USD 1 ANO"]
    for column in tmp:
        if column in df.columns:
            df[column] = df[column].replace({"-": None, "": None, "0": None})
            df[column] = pd.to_numeric(df[column], errors="coerce")
            df[column] = round(df[column], 2)
            df[column] = df[column].apply(lambda x: f"{x}%"
                                          if pd.notna(x) else x)

    tmp = ["NOME", "ATIVO"]
    df = _string_columns(df=df, columns=tmp)
    df.to_parquet("INVESTIDOR-10_ETFS_AUX.parquet")
    return df


class StocksBR:
    """
    Summary.

    Retrieve the brazilian stocks companies infos.
    """

    def __init__(self, ticket):
        self.ticket = ticket
        url = "https://investidor10.com.br/acoes/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if (page.status_code != 200 or
            soup.find("div", {"class": "basic_info"}) is None or
            soup.find("div",
                      {"class": "table grid-3",
                       "id": "table-indicators-company"}) is None or
            soup.find("section", id="cards-ticker") is None or
            soup.find("div", {"class": "table table-bordered outter-" +
                              "borderless",
                              "id": "table-indicators"}) is None):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self):
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        df = pd.DataFrame(tmp)
        df = _clean_cards(df=df)
        return df

    def _parse_company(self, soup):
        # Company 1.
        table = soup.find("div", {"class": "basic_info"})
        tmp = []
        for row in table.find_all("tr"):
            column = row.find_all("td")
            if column:
                title = column[0].text.upper().strip()
                value = column[1].text.upper().strip()
                tmp.append({"INFO": title, "VALOR": value})
        df1 = pd.DataFrame(tmp)  # Temporary dataframe.

        # Company 2.
        cells = soup.find("div", {"class": "table grid-3",
                                  "id": "table-indicators-company"})
        cells = cells.find_all("div", {"class": "cell"})
        tmp = []
        for cell in cells:
            title = cell.find("span", {"class": "title"})
            value1 = cell.find("div", {"class": "detail-value"})
            value2 = cell.find("span", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                tmp.append({"INFO": title, "VALOR": value1,
                            "VALOR2": value2})
        df2 = pd.DataFrame(tmp)  # Temporary dataframe.
        df2["VALOR"] = df2.apply(
            lambda row: row["VALOR"]
            if row["VALOR"] is not None else row["VALOR2"], axis=1)
        df2 = df2[["INFO", "VALOR"]]  # Necessary columns.
        company = pd.concat([df1, df2])
        company = _clean_cards(df=company)
        return company

    def _parse_price(self, soup):
        cells = soup.find("section", id="cards-ticker")
        cells = cells.select("._card")
        tmp = []
        for cell in cells:
            title = cell.select("._card-header span")
            value = cell.select("._card-body span")
            if title:
                title = (title[0].get("title").upper().strip()
                         if title and title[0].text else None)
                value = (value[0].get_text(strip=True).upper()
                         if value and value[0].text else None)
                tmp.append({"INFO": title, "VALOR": value})
        price = pd.DataFrame(tmp)
        # Removing unnecessary row if any.
        price = price.drop([2, 3, 4], errors="ignore")
        price = _clean_cards(df=price)
        return price

    def _parse_kpi(self, soup):
        cells = soup.find("div",
                          {"class": "table table-bordered outter-" +
                           "borderless", "id": "table-indicators"})
        cells = cells.find_all("div", {"class": "cell"})
        tmp = []
        for cell in cells:
            title = cell.find("span",
                              {"class": "d-flex justify-content-between " +
                               "align-items-center"})
            value = cell.find("div",
                              {"class": "value d-flex justify-content-" +
                               "between align-items-center"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title, "VALOR": value})
        kpi = pd.DataFrame(tmp)
        kpi = _clean_cards(df=kpi)
        return kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "Nº TOTAL DE PAPEIS": "QUANTIDADE DE PAPÉIS",
            "P/CAP.GIRO": "P/CAPITAL DE GIRO", "CNPJ:": "CNPJ",
            "LIQUIDEZ MÉDIA DIÁRIA": "LIQUIDEZ", "NOME DA EMPRESA:": "EMPRESA",
            "P/ATIVO CIRC LIQ": "P/ATIVO CIRCULANTE LÍQUIDO",
            "P/RECEITA (PSR)": "P/RECEITA LÍQUIDA",
            "VARIAÇÃO (12M)": "VARIAÇÃO DE COTAÇÃO 1 ANO",
            "PATRIMÔNIO/ATIVOS": "PATRIMÔNIO LÍQUIDO/ATIVOS",
            "DÍVIDA LÍQUIDA/PATRIMÔNIO": "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO",
            "DÍVIDA BRUTA/PATRIMÔNIO": "DÍVIDA BRUTA/PATRIMÔNIO LÍQUIDO",
            "ANO DE ESTREIA NA BOLSA:": "ANO IPO",
            "ANO DE FUNDAÇÃO:": "ANO FUNDAÇÃO",
            "NÚMERO DE FUNCIONÁRIOS:": "QUANTIDADE DE FUNCIONÁRIOS"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the brazilian stocks infos.
        """
        soup = self._get_soup()[0]
        df1 = self._parse_common_data()
        df2 = self._parse_company(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "EMPRESA", "CNPJ", "ANO IPO", "ANO FUNDAÇÃO", "SETOR",
               "SEGMENTO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        df = _string_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the brazilian stocks prices infos.
        """
        soup = self._get_soup()[0]
        df1 = self._parse_common_data()
        df1 = _clean_cards(df1)
        df2 = self._parse_price(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO", "VARIAÇÃO DE COTAÇÃO 1 ANO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["VARIAÇÃO DE COTAÇÃO 1 ANO"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self):
        """
        Summary.

        Function to retrieve the brazilian stocks kpis infos.
        """
        soup = self._get_soup()[0]
        df1 = self._parse_common_data()
        df1 = _clean_cards(df1)
        df2 = self._parse_company(soup)
        df3 = self._parse_kpi(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "VALOR DE MERCADO", "VALOR DE FIRMA", "P/L",
               "P/VP", "P/EBITDA", "P/EBIT", "EV/EBITDA", "EV/EBIT",
               "P/RECEITA LÍQUIDA", "P/ATIVO", "P/CAPITAL DE GIRO",
               "P/ATIVO CIRCULANTE LÍQUIDO", "ROE", "ROIC", "ROA",
               "MARGEM LÍQUIDA", "MARGEM BRUTA", "MARGEM EBIT",
               "MARGEM EBITDA", "DIVIDEND YIELD", "PAYOUT", "DÍVIDA LÍQUIDA",
               "DÍVIDA BRUTA", "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO",
               "DÍVIDA LÍQUIDA/EBITDA", "DÍVIDA LÍQUIDA/EBIT",
               "DÍVIDA BRUTA/PATRIMÔNIO LÍQUIDO", "LIQUIDEZ CORRENTE",
               "LIQUIDEZ", "PASSIVOS/ATIVOS", "CAGR RECEITAS 5 ANOS",
               "CAGR LUCROS 5 ANOS", "QUANTIDADE DE FUNCIONÁRIOS",
               "QUANTIDADE DE PAPÉIS", "ATIVOS", "ATIVO CIRCULANTE",
               "DISPONIBILIDADE", "FREE FLOAT", "TAG ALONG", "VPA", "LPA",
               "GIRO ATIVOS"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["FREE FLOAT", "TAG ALONG", "DIVIDEND YIELD", "PAYOUT", "ROA",
               "ROE", "ROIC", "CAGR LUCROS 5 ANOS", "TICKET", "MOEDA",
               "MARGEM LÍQUIDA", "MARGEM BRUTA", "MARGEM EBIT",
               "MARGEM EBITDA", "CAGR RECEITAS 5 ANOS"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["VALOR DE MERCADO", "VALOR DE FIRMA", "PATRIMÔNIO LÍQUIDO",
               "QUANTIDADE DE PAPÉIS", "ATIVOS", "ATIVO CIRCULANTE",
               "DÍVIDA BRUTA", "DÍVIDA LÍQUIDA", "DISPONIBILIDADE", "LIQUIDEZ",
               "P/L", "P/VP", "EV/EBIT", "P/EBIT", "P/ATIVO", "GIRO ATIVOS",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO", "VPA", "LPA",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "PASSIVOS/ATIVOS",
               "DÍVIDA BRUTA/PATRIMÔNIO LÍQUIDO", "LIQUIDEZ CORRENTE",
               "PATRIMÔNIO LÍQUIDO/ATIVOS", "DÍVIDA LÍQUIDA/EBIT", "EV/EBITDA",
               "QUANTIDADE DE FUNCIONÁRIOS", "P/RECEITA LÍQUIDA", "P/EBITDA",
               "DÍVIDA LÍQUIDA/EBITDA"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
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
        df = df.drop(["INFO"], axis=1, errors="ignore")  # Removing column.

        tmp = ["COTAÇÃO", "VALOR DE MERCADO", "VALOR DE FIRMA", "P/EBITDA",
               "QUANTIDADE DE PAPÉIS", "ATIVOS", "ATIVO CIRCULANTE",
               "DÍVIDA BRUTA", "DÍVIDA LÍQUIDA", "DISPONIBILIDADE", "LIQUIDEZ",
               "P/L", "P/VP", "EV/EBIT", "P/EBIT", "P/ATIVO", "GIRO ATIVOS",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO", "VPA", "LPA",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "PASSIVOS/ATIVOS",
               "DÍVIDA BRUTA/PATRIMÔNIO LÍQUIDO", "LIQUIDEZ CORRENTE",
               "PATRIMÔNIO LÍQUIDO/ATIVOS", "DÍVIDA LÍQUIDA/EBIT", "EV/EBITDA",
               "QUANTIDADE DE FUNCIONÁRIOS", "P/RECEITA LÍQUIDA",
               "DÍVIDA LÍQUIDA/EBITDA", "PATRIMÔNIO LÍQUIDO"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VARIAÇÃO DE COTAÇÃO 1 ANO", "FREE FLOAT", "TAG ALONG",
               "DIVIDEND YIELD", "PAYOUT", "ROA", "ROE", "ROIC",
               "CAGR LUCROS 5 ANOS", "MARGEM LÍQUIDA", "MARGEM BRUTA",
               "MARGEM EBIT", "MARGEM EBITDA", "CAGR RECEITAS 5 ANOS"]
        for column in tmp:
            if column in df.columns:
                df[column] = df[column].str.replace("%", "", regex=False)
                df[column] = pd.to_numeric(df[column], errors="coerce")
        return df


class ReitsBR:
    """
    Summary.

    Retrieve the brazilian reits companies infos.
    """

    def __init__(self, ticket):
        self.ticket = ticket
        url = "https://investidor10.com.br/fiis/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if (page.status_code != 200 or
           soup.find_all("div", {"class": "cell"}) is None or
           soup.find("section", id="cards-ticker") is None):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self):
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        df = pd.DataFrame(tmp)
        df = _clean_cards(df=df)
        return df

    def _parse_company(self, soup):
        cells = soup.find_all("div", {"class": "cell"})
        tmp = []
        for cell in cells:
            title = cell.find("span", {"class": "name"})
            value = cell.find("div", {"class": "value"})
            if title and value:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
            tmp.append({"INFO": title, "VALOR": value})
        company = pd.DataFrame(tmp)  # Temporary dataframe.
        # company = company.drop([14], errors="ignore")  # Necessary rows.
        company = _clean_cards(df=company)
        return company

    def _parse_price(self, soup):
        cells = soup.find("section", id="cards-ticker")
        cells = cells.select("._card")
        tmp = []
        for cell in cells:
            title = cell.select("._card-header span")
            value = cell.select("._card-body span")
            if title:
                title = (title[0].get("title").upper().strip()
                         if title and title[0].text else None)
                value = (value[0].get_text(strip=True).upper()
                         if value and value[0].text else None)
            tmp.append({"INFO": title, "VALOR": value})
        price = pd.DataFrame(tmp)
        price = _clean_cards(df=price)
        return price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "RAZÃO SOCIAL": "NOME", "LIQUIDEZ DIÁRIA": "LIQUIDEZ",
            "TIPO DE FUNDO": "SETOR", "TIPO DE GESTÃO": "GESTÃO",
            "COTAS EMITIDAS": "QUANTIDADE DE COTAS",
            "TAXA DE ADMINISTRAÇÃO": "TAXA ADMINISTRATIVA",
            "NUMERO DE COTISTAS": "QUANTIDADE DE COTISTAS",
            "VAL. PATRIMONIAL P/ COTA": "VALOR PATRIMONIAL/COTA",
            "VARIAÇÃO (12M)": "VARIAÇÃO DE COTAÇÃO 1 ANO",
            "MANDATO": "TIPO ANBIMA"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the brazilian reits infos.
        """
        soup = self._get_soup()[0]
        df1 = self._parse_common_data()
        df2 = self._parse_company(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "NOME", "CNPJ", "PÚBLICO-ALVO", "TIPO ANBIMA",
               "SEGMENTO", "SETOR", "PRAZO DE DURAÇÃO", "GESTÃO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        df = _string_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the brazilian reits prices infos.
        """
        soup = self._get_soup()[0]
        df1 = self._parse_common_data()
        df1 = _clean_cards(df1)
        df2 = self._parse_company(soup)
        df3 = self._parse_price(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO", "VARIAÇÃO DE COTAÇÃO 1 ANO",
               "ÚLTIMO RENDIMENTO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VARIAÇÃO DE COTAÇÃO 1 ANO"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO", "ÚLTIMO RENDIMENTO"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self):
        """
        Summary.

        Function to retrieve the brazilian reits kpis infos.
        """
        soup = self._get_soup()[0]
        df1 = self._parse_common_data()
        df1 = _clean_cards(df1)
        df2 = self._parse_company(soup)
        df3 = self._parse_price(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "VALOR PATRIMONIAL/COTA",
               "VALOR PATRIMONIAL", "P/VP", "DIVIDEND YIELD", "LIQUIDEZ",
               "QUANTIDADE DE COTISTAS", "QUANTIDADE DE COTAS", "VACÂNCIA",
               "TAXA ADMINISTRATIVA"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VACÂNCIA", "DIVIDEND YIELD",
               "TAXA ADMINISTRATIVA"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["QUANTIDADE DE COTISTAS", "QUANTIDADE DE COTAS", "P/VP",
               "VALOR PATRIMONIAL/COTA"]
        df = _numeric_columns(df=df, columns=tmp)

        tmp = ["VALOR PATRIMONIAL", "LIQUIDEZ"]
        for column in tmp:
            if column in df.columns:
                df[column] = (df[column].str.replace("R$ ", "", regex=False)
                              .str.replace(".", "", regex=False)
                              .str.replace(",", ".", regex=False))

        df["VALOR PATRIMONIAL"] = df["VALOR PATRIMONIAL"].apply(_times)
        df["LIQUIDEZ"] = df["LIQUIDEZ"].apply(_times2)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self):
        """
        Summary.

        Function to aggregate the brazilian reits full infos.
        """
        df = pd.concat([self.info(), self.price(), self.kpi()])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        df = df.drop(["INFO"], axis=1, errors="ignore")  # Necessary rows.

        tmp = ["ÚLTIMO RENDIMENTO", "QUANTIDADE DE COTISTAS", "P/VP",
               "QUANTIDADE DE COTAS", "VALOR PATRIMONIAL/COTA", "COTAÇÃO",
               "VALOR PATRIMONIAL", "LIQUIDEZ"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VARIAÇÃO DE COTAÇÃO 1 ANO", "VACÂNCIA", "DIVIDEND YIELD"]
        for column in tmp:
            if column in df.columns:
                df[column] = df[column].str.replace("%", "", regex=False)
                df[column] = pd.to_numeric(df[column], errors="coerce")
        return df


class ETFsBR:
    """
    Summary.

    Retrieve the brazilian ETFs companies infos.
    """

    def __init__(self, ticket):
        self.ticket = ticket
        self.aux = pd.read_parquet("INVESTIDOR-10_ETFS-BR_AUX.parquet")
        url = "https://investidor10.com.br/etfs/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if (page.status_code != 200 or
           soup.find("section", id="cards-ticker") is None):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom):
        nome = dom.xpath("/html/body/div[4]/main/header/div[2]/div/" +
                         "div[1]/div[2]/h2")
        nome = (nome[0].text.upper().strip()
                if nome and nome[0].text else None)
        infos = []
        infos.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        infos.append({"INFO": "NOME", "VALOR": nome})
        infos.append({"INFO": "MOEDA", "VALOR": "BRL"})
        df = pd.DataFrame(infos)
        df = _clean_cards(df=df)
        return df

    def _parse_price(self, soup):
        cells = soup.find("section", id="cards-ticker")
        cells = cells.select(".br ._card")
        tmp = []
        for cell in cells:
            title = cell.select("._card-header span")
            value = cell.select("._card-body span")
            if title:
                title = (title[0].get("title").upper().strip()
                         if title and title[0].text else None)
                value = (value[0].get_text(strip=True).upper()
                         if value and value[0].text else None)
                tmp.append({"INFO": title, "VALOR": value})
        price = pd.DataFrame(tmp)
        price.reset_index(drop=True, inplace=True)  # Reseting index.
        price = _clean_cards(df=price)
        return price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "DY": "DIVIDEND YIELD", "CAPITALIZAÇÃO": "VALOR DE MERCADO",
            "VARIAÇÃO (12M)": "VARIAÇÃO DE COTAÇÃO 1 ANO",
            "VARIAÇÃO (60N)": "VARIAÇÃO DE COTAÇÃO 5 ANOS"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the brazilian ETFs infos.
        """
        dom = self._get_soup()[1]
        df = self._parse_common_data(dom)
        df = df.drop([2])  # Removing unnecessary rows.
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the brazilian ETFs prices infos.
        """
        soup, dom = self._get_soup()
        df1 = self.aux
        df1 = df1[df1["ATIVO"] == self.ticket.strip().upper()]
        df1 = df1[["VARIAÇÃO DE COTAÇÃO 1 MÊS"]]
        df1 = df1.reset_index(drop=True)
        df1 = df1.T.reset_index(drop=False)
        df1 = df1.rename(columns={"index": "INFO", 0: "VALOR"})
        df2 = self._parse_common_data(dom)
        df3 = self._parse_price(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO", "VARIAÇÃO DE COTAÇÃO 1 ANO",
               "VARIAÇÃO DE COTAÇÃO 5 ANOS"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VARIAÇÃO DE COTAÇÃO 1 ANO",
               "VARIAÇÃO DE COTAÇÃO 5 ANOS"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self):
        """
        Summary.

        Function to retrieve the brazilian ETFs kpis infos.
        """
        soup, dom = self._get_soup()
        df1 = self.aux
        df1 = df1[df1["ATIVO"] == self.ticket.strip().upper()]
        df1 = df1[["LIQUIDEZ"]]
        df1 = df1.reset_index(drop=True)
        df1 = df1.T.reset_index(drop=False)
        df1 = df1.rename(columns={"index": "INFO", 0: "VALOR"})
        df2 = self._parse_common_data(dom)
        df3 = self._parse_price(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "VALOR DE MERCADO", "LIQUIDEZ",
               "DIVIDEND YIELD"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["DIVIDEND YIELD"]
        df = _string_columns(df=df, columns=tmp)

        df["VALOR DE MERCADO"] = (df["VALOR DE MERCADO"]
                                  .str.replace("R$\n", "", regex=False))
        df["VALOR DE MERCADO"] = df["VALOR DE MERCADO"].apply(_times2)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self):
        """
        Summary.

        Function to aggregate the brazilian ETFs full infos.
        """
        df = pd.concat([self.info(), self.price(), self.kpi()])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        df = df.drop(["INFO"], axis=1, errors="ignore")  # Necessary rows.

        tmp = ["COTAÇÃO", "VALOR DE MERCADO", "LIQUIDEZ"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VARIAÇÃO DE COTAÇÃO 1 ANO", "VARIAÇÃO DE COTAÇÃO 5 ANOS",
               "DIVIDEND YIELD"]
        for column in tmp:
            if column in df.columns:
                df[column] = df[column].str.replace("%", "", regex=False)
                df[column] = pd.to_numeric(df[column], errors="coerce")
        return df


class StocksReits:
    """
    Summary.

    Retrieve the stocks and reits companies infos.
    """

    def __init__(self, ticket, type_asset):
        self.ticket = ticket
        if type_asset == "STOCKS":
            urls = "https://investidor10.com.br/stocks/{}"
            self.url = urls.format(ticket.lower())
        elif type_asset == "REITS":
            urlr = "https://investidor10.com.br/reits/{}"
            self.url = urlr.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if (page.status_code != 200 or
            soup.find("div", {"class": "basic_info"}) is None or
            soup.find("div", {"class": "table grid-3",
                              "id": "table-indicators-company"}) is None or
            soup.find("section", id="cards-ticker") is None or
            soup.find("div", {"class": "table table-bordered outter-" +
                              "borderless three_columns",
                              "id": "table-indicators"}) is None):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom):
        empresa = dom.xpath("/html/body/div[4]/main/header/div[2]/div/" +
                            "div[1]/div[2]/h2")
        empresa = (empresa[0].text.upper().strip()
                   if empresa and empresa[0].text else None)
        cotacao_brl = dom.xpath("/html/body/div[4]/main/section/div/" +
                                "section[1]/div[1]/div[2]/div/span[2]")
        cotacao_brl = (cotacao_brl[0].text.upper().strip()
                       if cotacao_brl and cotacao_brl[0].text else None)
        infos = []
        infos.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        # infos.append({"INFO": "EMPRESA", "VALOR": empresa})
        infos.append({"INFO": "MOEDA", "VALOR": "USD"})
        infos.append({"INFO": "COTAÇÃO BRL", "VALOR": cotacao_brl})
        df = pd.DataFrame(infos)
        df = _clean_cards(df=df)
        return df

    def _parse_company(self, soup):
        # Company 1.
        table = soup.find("div", {"class": "basic_info"})
        tmp = []
        for row in table.find_all("tr"):
            column = row.find_all("td")
            if column:
                title = column[0].text.upper().strip()
                value = column[1].text.upper().strip()
                tmp.append({"INFO": title, "VALOR": value})
        df1 = pd.DataFrame(tmp)  # Temporary dataframe.

        # Company 2.
        cells = soup.find("div", {"class": "table grid-3",
                                  "id": "table-indicators-company"})
        cells = cells.find_all("div", {"class": "cell"})
        tmp = []
        for cell in cells:
            title = cell.find("h3", {"class": "title"})
            value1 = cell.find("h4", {"class": "detail-value"})
            value2 = cell.find("h4", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                tmp.append({"INFO": title, "VALOR": value1, "VALOR2": value2})
        df2 = pd.DataFrame(tmp)  # Temporary dataframe.
        df2["VALOR"] = df2.apply(
            lambda row: row["VALOR"]
            if row["VALOR"] is not None else row["VALOR2"], axis=1)
        df2 = df2[["INFO", "VALOR"]]  # Necessary columns.
        company = pd.concat([df1, df2])
        company = _clean_cards(df=company)
        return company

    def _parse_price(self, soup):
        cells = soup.find("section", id="cards-ticker")
        cells = cells.select("._card")
        tmp = []
        for cell in cells:
            title = cell.select("._card-header h2")
            value = cell.select("._card-body span")
            if title:
                title = (title[0].get("title").upper().strip()
                         if title and title[0].text else None)
                value = (value[0].get_text(strip=True).upper()
                         if value and value[0].text else None)
                tmp.append({"INFO": title, "VALOR": value})
        price = pd.DataFrame(tmp)
        price = price.drop([2, 3, 4],
                           errors="ignore")  # Removing unnecessary row if any.
        price = _clean_cards(df=price)
        return price

    def _parse_kpi(self, soup):
        cells = soup.find("div",
                          {"class": "table table-bordered outter-" +
                           "borderless three_columns",
                           "id": "table-indicators"})
        cells = cells.find_all("div", {"class": "cell"})
        tmp = []
        for cell in cells:
            title = cell.find("h3",
                              {"class": "d-flex justify-content-between " +
                               "align-items-center"})
            value = cell.find("div",
                              {"class": "value d-flex justify-content-" +
                               "between align-items-center"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title, "VALOR": value})
        kpi = pd.DataFrame(tmp)  # Temporary dataframe.
        kpi = _clean_cards(df=kpi)
        return kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "Nº TOTAL DE PAPEIS": "QUANTIDADE DE PAPÉIS", "CEO:": "CEO",
            "INDÚSTRIA": "SUBSETOR", "SETOR": "SETOR",
            "P/RECEITA (PSR)": "P/RECEITA LÍQUIDA", "PAÍS DE ORIGEM:": "PAÍS",
            "VOLUME MÉDIO DE NEGOCIAÇÕES DIÁRIA": "LIQUIDEZ USD",
            "COTAÇÃO": "COTAÇÃO USD", "ATIVOS": "ATIVOS USD",
            "VALOR DE MERCADO": "VALOR DE MERCADO USD",
            "PATRIMÔNIO LÍQUIDO": "PATRIMÔNIO LÍQUIDO USD",
            "VARIAÇÃO (12M)": "VARIAÇÃO DE COTAÇÃO USD 1 ANO",
            "PATRIMÔNIO/ATIVOS": "PATRIMÔNIO LÍQUIDO/ATIVOS",
            "NOME DA EMPRESA:": "EMPRESA", "ANO DE FUNDAÇÃO:": "ANO FUNDAÇÃO",
            "ANO DE ESTREIA NA BOLSA:": "ANO IPO",
            "NÚMERO DE FUNCIONÁRIOS:": "QUANTIDADE DE FUNCIONÁRIOS"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the stocks and reits infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_company(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "EMPRESA", "ANO IPO", "ANO FUNDAÇÃO", "PAÍS", "SETOR",
               "SUBSETOR", "CEO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        df = _string_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the stocks and reits prices infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_price(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO USD", "COTAÇÃO BRL"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VARIAÇÃO DE COTAÇÃO USD 1 ANO"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO USD", "COTAÇÃO BRL"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self):
        """
        Summary.

        Function to retrieve the stocks and reits kpis infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_company(soup)
        df3 = self._parse_kpi(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "P/L", "P/RECEITA LÍQUIDA", "P/VP",
               "P/EBITDA", "P/EBIT", "P/ATIVO", "DIVIDEND YIELD", "ROA", "ROE",
               "ROIC", "MARGEM LÍQUIDA", "MARGEM BRUTA", "MARGEM OPERACIONAL",
               "CAGR RECEITAS 5 ANOS", "CAGR LUCROS 5 ANOS", "VPA", "LPA",
               "VALOR DE MERCADO USD", "PATRIMÔNIO LÍQUIDO USD", "ATIVOS USD",
               "LIQUIDEZ USD", "PATRIMÔNIO LÍQUIDO/ATIVOS",
               "QUANTIDADE DE PAPÉIS", "QUANTIDADE DE FUNCIONÁRIOS"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["DIVIDEND YIELD", "ROA", "ROE", "ROIC", "MARGEM LÍQUIDA",
               "MARGEM BRUTA", "MARGEM OPERACIONAL", "CAGR RECEITAS 5 ANOS",
               "CAGR LUCROS 5 ANOS", "TICKET", "MOEDA"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["VALOR DE MERCADO USD", "PATRIMÔNIO LÍQUIDO USD", "P/EBITDA",
               "ATIVOS USD", "QUANTIDADE DE PAPÉIS", "LIQUIDEZ USD", "P/L",
               "P/RECEITA LÍQUIDA", "P/VP", "P/EBIT", "P/ATIVO", "VPA", "LPA",
               "PATRIMÔNIO LÍQUIDO/ATIVOS", "QUANTIDADE DE FUNCIONÁRIOS"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self):
        """
        Summary.

        Function to aggregate the brazilian stocks and reits full infos.
        """
        df = pd.concat([self.info(), self.price(), self.kpi()])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        df = df.drop(["INFO"], axis=1, errors="ignore")  # Necessary rows.

        tmp = ["COTAÇÃO USD", "COTAÇÃO BRL", "VALOR DE MERCADO USD",
               "PATRIMÔNIO LÍQUIDO USD", "P/EBITDA", "ATIVOS USD",
               "QUANTIDADE DE PAPÉIS", "LIQUIDEZ USD", "P/L",
               "P/RECEITA LÍQUIDA", "P/VP", "P/EBIT", "P/ATIVO", "VPA", "LPA",
               "PATRIMÔNIO LÍQUIDO/ATIVOS", "QUANTIDADE DE FUNCIONÁRIOS"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VARIAÇÃO DE COTAÇÃO USD 1 ANO", "DIVIDEND YIELD", "ROA", "ROE",
               "ROIC", "MARGEM LÍQUIDA", "MARGEM BRUTA", "MARGEM OPERACIONAL",
               "CAGR RECEITAS 5 ANOS", "CAGR LUCROS 5 ANOS"]
        for column in tmp:
            if column in df.columns:
                df[column] = df[column].str.replace("%", "", regex=False)
                df[column] = pd.to_numeric(df[column], errors="coerce")
        return df


class ETFs:
    """
    Summary.

    Retrieve the ETFs companies infos.
    """

    def __init__(self, ticket):
        self.ticket = ticket
        self.aux = pd.read_parquet("INVESTIDOR-10_ETFS_AUX.parquet")
        url = "https://investidor10.com.br/etfs-global/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if (page.status_code != 200 or
           soup.find("section", id="cards-ticker") is None):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom):
        nome = dom.xpath("/html/body/div[4]/main/header/div[2]/div/" +
                         "div[1]/div[2]/h2")
        nome = (nome[0].text.upper().strip()
                if nome and nome[0].text else None)
        cotacao_brl = dom.xpath("/html/body/div[4]/main/section/div/" +
                                "section[1]/div[1]/div[2]/div/span[2]")
        cotacao_brl = (cotacao_brl[0].text.upper().strip()
                       if cotacao_brl and cotacao_brl[0].text else None)
        infos = []
        infos.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        infos.append({"INFO": "NOME", "VALOR": nome})
        infos.append({"INFO": "MOEDA", "VALOR": "USD"})
        infos.append({"INFO": "COTAÇÃO BRL", "VALOR": cotacao_brl})
        df = pd.DataFrame(infos)
        df = _clean_cards(df=df)
        return df

    def _parse_price(self, soup):
        # Price.
        cells = soup.find("section", id="cards-ticker")
        cells = cells.select(".global ._card")
        tmp = []
        for cell in cells:
            title = cell.select("._card-header span")
            value = cell.select("._card-body span")
            if title:
                title = (title[0].get("title").upper().strip()
                         if title and title[0].text else None)
                value = (value[0].get_text(strip=True).upper()
                         if value and value[0].text else None)
                tmp.append({"INFO": title, "VALOR": value})
        price = pd.DataFrame(tmp)
        price.reset_index(drop=True, inplace=True)  # Reseting index.
        price = _clean_cards(df=price)
        return price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "COTAÇÃO": "COTAÇÃO USD", "DY": "DIVIDEND YIELD",
            "CAPITALIZAÇÃO": "VALOR DE MERCADO USD",
            "VARIAÇÃO (12M)": "VARIAÇÃO DE COTAÇÃO USD 1 ANO",
            "VARIAÇÃO (60N)": "VARIAÇÃO DE COTAÇÃO USD 5 ANOS"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the brazilian ETFs infos.
        """
        dom = self._get_soup()
        df = self._parse_common_data(dom)
        df = df.drop([2, 3])  # Removing unnecessary rows.
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the brazilian ETFs prices infos.
        """
        soup, dom = self._get_soup()
        df1 = self.aux
        df1 = df1[df1["ATIVO"] == self.ticket.strip().upper()]
        df1 = df1[["VARIAÇÃO DE COTAÇÃO USD 1 MÊS"]]
        df1 = df1.reset_index(drop=True)
        df1 = df1.T.reset_index(drop=False)
        df1 = df1.rename(columns={"index": "INFO", 0: "VALOR"})
        df2 = self._parse_common_data(dom, )
        df3 = self._parse_price(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO BRL", "COTAÇÃO USD",
               "VARIAÇÃO DE COTAÇÃO USD 1 ANO",
               "VARIAÇÃO DE COTAÇÃO USD 5 ANOS"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VARIAÇÃO DE COTAÇÃO USD 1 ANO",
               "VARIAÇÃO DE COTAÇÃO USD 5 ANOS"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO BRL", "COTAÇÃO USD"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self):
        """
        Summary.

        Function to retrieve the brazilian ETFs kpis infos.
        """
        soup, dom = self._get_soup()
        df1 = self.aux
        df1 = df1[df1["ATIVO"] == self.ticket.strip().upper()]
        df1 = df1[["LIQUIDEZ USD"]]
        df1 = df1.reset_index(drop=True)
        df1 = df1.T.reset_index(drop=False)
        df1 = df1.rename(columns={"index": "INFO", 0: "VALOR"})
        df2 = self._parse_common_data(dom)
        df3 = self._parse_price(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "VALOR DE MERCADO USD", "LIQUIDEZ USD",
               "DIVIDEND YIELD"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "DIVIDEND YIELD"]
        df = _string_columns(df=df, columns=tmp)

        df["VALOR DE MERCADO USD"] = (df["VALOR DE MERCADO USD"]
                                      .str.replace("US$\n", "", regex=False))
        df["VALOR DE MERCADO USD"] = df["VALOR DE MERCADO USD"].apply(_times2)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self):
        """
        Summary.

        Function to aggregate the brazilian ETFs full infos.
        """
        df = pd.concat([self.info(), self.price(), self.kpi()])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        df = df.drop(["INFO"], axis=1, errors="ignore")  # Necessary rows.

        tmp = ["COTAÇÃO BRL", "COTAÇÃO USD", "VALOR DE MERCADO USD",
               "LIQUIDEZ USD"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VARIAÇÃO DE COTAÇÃO USD 1 ANO", "DIVIDEND YIELD",
               "VARIAÇÃO DE COTAÇÃO USD 5 ANOS"]
        for column in tmp:
            if column in df.columns:
                df[column] = df[column].str.replace("%", "", regex=False)
                df[column] = pd.to_numeric(df[column], errors="coerce")
        return df
