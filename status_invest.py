"""
Summary.

Retrieve the companies infos from Status Invest website.
"""
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

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
                                               "CAGR DIVIDENDOS 3 ANOS",
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


class StocksBR:
    """
    Summary.

    Retrieve the brazilian stocks companies infos.
    """

    def __init__(self, ticket):
        self.ticket = ticket
        url = "https://statusinvest.com.br/acoes/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom):
        cnpj = dom.xpath("/html/body/main/div[5]/div[1]/div/div[1]/div[2]/" +
                         "h4/small")
        cnpj = (cnpj[0].text.strip() if cnpj and cnpj[0].text else None)
        tag_along = dom.xpath("/html/body/main/div[2]/div/div[5]/div/" +
                              "div/div[2]/div/div/div/strong")
        tag_along = (tag_along[0].text.strip()
                     if tag_along and tag_along[0].text else None)
        empresa = dom.xpath("/html/body/main/div[5]/div[1]/div/div[1]/" +
                            "div[2]/h4/span")
        empresa = (empresa[0].text.strip().upper()
                   if empresa and empresa[0].text else None)
        tipo_ativo1 = dom.xpath("/html/body/main/div[2]/div/div[5]/div/" +
                                "div/div[1]/div/div/h3/strong")
        tipo_ativo2 = dom.xpath("/html/body/main/div[2]/div/div[5]/div/" +
                                "div/div[1]/div/div/strong")
        tipo_ativo = (tipo_ativo1[0].text.strip().upper()
                      if tipo_ativo1 and tipo_ativo1[0].text
                      else tipo_ativo2[0].text.strip().upper()
                      if tipo_ativo2 and tipo_ativo2[0].text else
                      None)
        liquidez = dom.xpath("/html/body/main/div[2]/div/div[5]/div/div/" +
                             "div[3]/div/div/div/strong")
        liquidez = (liquidez[0].text.strip().upper()
                    if liquidez and liquidez[0].text else None)
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        tmp.append({"INFO": "EMPRESA", "VALOR": empresa})
        tmp.append({"INFO": "CNPJ", "VALOR": cnpj})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        tmp.append({"INFO": "TIPO ATIVO", "VALOR": tipo_ativo})
        tmp.append({"INFO": "TAG ALONG", "VALOR": tag_along})
        tmp.append({"INFO": "LIQUIDEZ", "VALOR": liquidez})
        df = pd.DataFrame(tmp)
        df = _clean_cards(df=df)
        return df

    def _parse_company(self, soup):
        # Company 1.
        cells = soup.find("div",
                          {"class": "top-info info-3 sm d-flex " +
                           "justify-between mb-3"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        for cell in cells:
            title = cell.find("h3", {"class": "title"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title, "VALOR": value})
        df1 = pd.DataFrame(tmp)
        df1.at[0, "INFO"] = "PATRIMÔNIO LÍQUIDO"  # Ranaming cell.

        # Company 2.
        cells = soup.find("div",
                          {"class": "card bg-main-gd-h white-text " +
                           "rounded ov-hidden pt-0 pb-0"})
        cells2 = cells.find_all("div", {"class": "info pr-md-2"}) + \
            cells.find_all("div", {"class": "info pl-md-2 pr-md-2"}) + \
            cells.find_all("div", {"class": "info pl-md-2"})
        tmp = []
        for cell in cells2:
            title = cell.find("span", {"class": "sub-value"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title, "VALOR": value})
        df2 = pd.DataFrame(tmp)
        company = pd.concat([df1, df2])
        company = _clean_cards(df=company)
        return company

    def _parse_price(self, soup):
        cells = soup.find("div",
                          {"class": "top-info has-special d-flex " +
                           "justify-between flex-wrap"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        tmp2 = []
        for cell in cells:  # Getting elements.
            title1 = cell.find("h3", {"class": "title"})
            title2 = cell.find("span", {"class": "sub-title"})
            value1 = cell.find("strong", {"class": "value"})
            value2 = cell.find("span", {"class": "sub-value"})
            if title1 or title2:
                title1 = (title1.get_text(strip=True).upper()
                          if title1 else None)
                title2 = (title2.get_text(strip=True).upper()
                          if title2 else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                tmp.append({"INFO": title1, "VALOR": value1})
                tmp2.append({"INFO": title2, "VALOR": value2})
        price = pd.concat([pd.DataFrame(tmp), pd.DataFrame(tmp2)])
        price.reset_index(drop=True, inplace=True)  # Reseting index.
        price = price.drop([3])  # Removing unnecessary rows.
        price = _clean_cards(df=price)
        return price

    def _parse_kpi(self, soup):
        cells = soup.find("div", {"class": "d-flex flex-wrap"})
        cells2 = cells.find_all("div",
                                {"class": "w-50 w-sm-33 w-md-25 " +
                                 "w-lg-16_6 mb-2 mt-2 item"}) + \
            cells.find_all("div",
                           {"class": "w-50 w-sm-33 w-md-25 w-lg-50 " +
                            "mb-2 mt-2 item"})
        tmp = []
        for cell in cells2:
            title1 = cell.find("h3", {"class": "title m-0 uppercase"})
            title2 = cell.find("h3", {"class": "title m-0 mr-1 uppercase"})
            value = cell.find("strong", {"class": "value"})
            if title1 or title2:
                title1 = (title1.get_text(strip=True).upper()
                          if title1 else None)
                title2 = (title2.get_text(strip=True).upper()
                          if title2 else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title1, "VALOR": title2, "VALOR2": value})
        kpi = pd.DataFrame(tmp)
        kpi["INFO"] = kpi.apply(
            lambda row: row["INFO"]
            if row["INFO"] is not None else row["VALOR"], axis=1)
        kpi = kpi[["INFO", "VALOR2"]]  # Necessary columns.
        kpi = kpi.rename(columns={"VALOR2": "VALOR"})  # Renaming columns.
        kpi = _clean_cards(df=kpi)
        return kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "VALOR ATUAL": "COTAÇÃO", "SETOR DE ATUAÇÃO": "SETOR",
            "MIN. 52 SEMANAS": "COTAÇÃO MÍNIMA 1 ANO",
            "MÁX. 52 SEMANAS": "COTAÇÃO MÁXIMA 1 ANO",
            "VALORIZAÇÃO (12M)": "VALORIZAÇÃO DE COTAÇÃO 1 ANO",
            "MIN. MÊS": "COTAÇÃO MÍNIMA 1 MÊS", "M. LÍQUIDA": "MARGEM LÍQUIDA",
            "MÁX. MÊS": "COTAÇÃO MÁXIMA 1 MÊS", "M. BRUTA": "MARGEM BRUTA",
            "ÚLTIMOS 12 MESES": "DIVIDENDOS PAGOS 1 ANO",
            "MÊS ATUAL": "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
            "Nº TOTAL DE PAPÉIS": "QUANTIDADE DE PAPÉIS",
            "SUBSETOR DE ATUAÇÃO": "SUBSETOR", "M. EBITDA": "MARGEM EBITDA",
            "SEGMENTO DE ATUAÇÃO": "SEGMENTO", "M. EBIT": "MARGEM EBIT",
            "P/SR": "P/RECEITA LÍQUIDA", "D.Y": "DIVIDEND YIELD",
            "P/CAP. GIRO": "P/CAPITAL DE GIRO",
            "P/ATIVO CIRC. LIQ.": "P/ATIVO CIRCULANTE LÍQUIDO",
            "DÍV. LÍQUIDA/PL": "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO",
            "DÍV. LÍQUIDA/EBITDA": "DÍVIDA LÍQUIDA/EBITDA",
            "DÍV. LÍQUIDA/EBIT": "DÍVIDA LÍQUIDA/EBIT",
            "PL/ATIVOS": "PATRIMÔNIO LÍQUIDO/ATIVOS",
            "LIQ. CORRENTE": "LIQUIDEZ CORRENTE"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the brazilian stocks infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_company(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "EMPRESA", "CNPJ", "TIPO ATIVO",
               "SEGMENTO DE LISTAGEM", "SETOR", "SUBSETOR", "SEGMENTO"]
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
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df1 = _clean_cards(df1)
        df2 = self._parse_price(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO", "COTAÇÃO MÍNIMA 1 MÊS",
               "COTAÇÃO MÁXIMA 1 MÊS", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
               "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO 1 ANO", "DIVIDENDOS PAGOS 1 ANO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
               "VALORIZAÇÃO DE COTAÇÃO 1 ANO"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS",
               "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "DIVIDENDOS PAGOS 1 ANO"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self):
        """
        Summary.

        Function to retrieve the brazilian stocks kpis infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df1 = _clean_cards(df1)
        df2 = self._parse_company(soup)
        df3 = self._parse_kpi(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "PATRIMÔNIO LÍQUIDO", "VALOR DE MERCADO",
               "VALOR DE FIRMA", "DÍVIDA LÍQUIDA", "DÍVIDA LÍQUIDA/EBITDA",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "ROE", "ROA", "ROIC",
               "MARGEM LÍQUIDA", "MARGEM EBITDA", "MARGEM EBIT",
               "CAGR LUCROS 5 ANOS", "CAGR RECEITAS 5 ANOS", "P/L", "P/VP",
               "EV/EBITDA", "EV/EBIT", "P/EBITDA", "P/EBIT",
               "P/RECEITA LÍQUIDA", "LIQUIDEZ CORRENTE", "PASSIVOS/ATIVOS",
               "ATIVOS", "ATIVO CIRCULANTE", "DISPONIBILIDADE", "DÍVIDA BRUTA",
               "FREE FLOAT", "DIVIDEND YIELD", "QUANTIDADE DE PAPÉIS",
               "TAG ALONG", "P/ATIVO", "P/CAPITAL DE GIRO",
               "P/ATIVO CIRCULANTE LÍQUIDO", "VPA", "GIRO ATIVOS",
               "MARGEM BRUTA", "LPA", "PEG RATIO", "DÍVIDA LÍQUIDA/EBIT",
               "PATRIMÔNIO LÍQUIDO/ATIVOS", "LIQUIDEZ"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["EMPRESA", "DIVIDEND YIELD", "MARGEM BRUTA", "ROIC", "ROA",
               "MARGEM EBITDA", "MARGEM EBIT", "MARGEM LÍQUIDA", "ROE",
               "CAGR RECEITAS 5 ANOS", "CAGR LUCROS 5 ANOS", "FREE FLOAT",
               "TAG ALONG", "TICKET", "MOEDA"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["PATRIMÔNIO LÍQUIDO", "ATIVOS", "ATIVO CIRCULANTE",
               "DÍVIDA BRUTA", "DISPONIBILIDADE", "DÍVIDA LÍQUIDA",
               "VALOR DE MERCADO", "VALOR DE FIRMA", "QUANTIDADE DE PAPÉIS",
               "P/L", "PEG RATIO", "P/VP", "EV/EBITDA", "EV/EBIT", "P/EBITDA",
               "P/EBIT", "VPA", "P/ATIVO", "LPA", "P/RECEITA LÍQUIDA",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "DÍVIDA LÍQUIDA/EBITDA",
               "DÍVIDA LÍQUIDA/EBIT", "PATRIMÔNIO LÍQUIDO/ATIVOS",
               "PASSIVOS/ATIVOS", "LIQUIDEZ CORRENTE", "GIRO ATIVOS",
               "LIQUIDEZ"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self,):
        """
        Summary.

        Function to aggregate the brazilian stocks full infos.
        """
        df = pd.concat([self.info(), self.price(), self.kpi()])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        df = df.drop(["INFO"], axis=1, errors="ignore")  # Necessary rows.

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS",
               "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO", "LIQUIDEZ",
               "DIVIDENDOS PAGOS 1 ANO", "PATRIMÔNIO LÍQUIDO", "ATIVOS",
               "DÍVIDA BRUTA", "DISPONIBILIDADE", "DÍVIDA LÍQUIDA",
               "VALOR DE MERCADO", "VALOR DE FIRMA", "QUANTIDADE DE PAPÉIS",
               "P/L", "PEG RATIO", "P/VP", "EV/EBITDA", "EV/EBIT", "P/EBITDA",
               "P/EBIT", "VPA", "P/ATIVO", "LPA", "P/RECEITA LÍQUIDA",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "DÍVIDA LÍQUIDA/EBITDA",
               "DÍVIDA LÍQUIDA/EBIT", "PATRIMÔNIO LÍQUIDO/ATIVOS",
               "PASSIVOS/ATIVOS", "LIQUIDEZ CORRENTE", "GIRO ATIVOS",
               "ATIVO CIRCULANTE"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VALORIZAÇÃO DE COTAÇÃO 1 MÊS", "VALORIZAÇÃO DE COTAÇÃO 1 ANO",
               "DIVIDEND YIELD", "MARGEM BRUTA", "ROIC", "ROA", "FREE FLOAT",
               "MARGEM EBITDA", "MARGEM EBIT", "MARGEM LÍQUIDA", "ROE",
               "CAGR RECEITAS 5 ANOS", "CAGR LUCROS 5 ANOS", "TAG ALONG"]
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
        url = "https://statusinvest.com.br/fundos-imobiliarios/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom):
        administrador = dom.xpath("/html/body/main/div[3]/div/div/" +
                                  "div[3]/div/div[2]/div[1]/div/strong")
        administrador = (administrador[0].text.upper().strip()
                         if administrador and administrador[0].text
                         else None)
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        tmp.append({"INFO": "ADMINISTRADOR", "VALOR": administrador})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        df = pd.DataFrame(tmp)
        df = _clean_cards(df=df)
        return df

    def _parse_company(self, soup):
        # Company 1.
        cells = soup.find("div",
                          {"class": "top-info top-info-1 top-info-md-2 " +
                           "sm d-flex justify-between"})
        cells = cells.find_all("div", {"class": "info"})
        info = []
        for cell in cells:  # Getting elements.
            title = cell.find("h3", {"class": "title m-0"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                info.append({"INFO": title, "VALOR": value})
        df1 = pd.DataFrame(info)  # Temporary dataframe.

        # Company 2.
        cells = soup.find("div",
                          {"class": "top-info top-info-1 top-info-sm-2 " +
                           "top-info-md-n sm d-flex justify-between"})
        cells = cells.find_all("div", {"class": "info"})
        info = []
        for cell in cells:  # Getting elements.
            title = cell.find("span", {"class": "sub-value"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                info.append({"INFO": title, "VALOR": value})
        df2 = pd.DataFrame(info)

        # Company 3.
        cells = soup.find("div",
                          {"class": "top-info top-info-2 top-info-md-n " +
                           "width-auto sm d-flex justify-between"})
        cells = cells.find_all("div", {"class": "info"})
        info = []
        for cell in cells:  # Getting elements.
            title = cell.find("span", {"class": "d-none"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                info.append({"INFO": title, "VALOR": value})
        df3 = pd.DataFrame(info)
        company = pd.concat([df1, df2, df3])
        company = _clean_cards(df=company)
        return company

    def _parse_price(self, soup):
        cells = soup.find("div",
                          {"class": "top-info d-flex flex-wrap " +
                           "justify-between mb-3 mb-md-5"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        tmp2 = []
        for cell in cells:  # Getting elements.
            title1 = cell.find("h3", {"class": "title"})
            title2 = cell.find("span", {"class": "sub-title"})
            value1 = cell.find("strong", {"class": "value"})
            value2 = cell.find("span", {"class": "sub-value"})
            if title1 or title2:
                title1 = (title1.get_text(strip=True).upper()
                          if title1 else None)
                title2 = (title2.get_text(strip=True).upper()
                          if title2 else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                tmp.append({"INFO": title1, "VALOR": value1})
                tmp2.append({"INFO": title2, "VALOR": value2})
        price = pd.concat([pd.DataFrame(tmp), pd.DataFrame(tmp2)])
        price = _clean_cards(df=price)
        return price

    def _parse_kpi(self, soup):
        cells = soup.find("div",
                          {"class": "top-info top-info-2 top-info-md-3 " +
                           "top-info-lg-n d-flex justify-between"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        tmp2 = []
        for cell in cells:  # Getting elements.
            title1 = cell.find("h3", {"class": "title"})
            title2 = cell.find("span", {"class": "sub-title"})
            value1 = cell.find("strong", {"class": "value"})
            value2 = cell.find("span", {"class": "sub-value"})
            if title1 or title2:
                title1 = (title1.get_text(strip=True).upper()
                          if title1 else None)
                title2 = (title2.get_text(strip=True).upper()
                          if title2 else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                tmp.append({"INFO": title1, "VALOR": value1})
                tmp2.append({"INFO": title2, "VALOR": value2})
        kpi = pd.concat([pd.DataFrame(tmp), pd.DataFrame(tmp2)])
        kpi.reset_index(drop=True, inplace=True)  # Reseting index.
        kpi = _clean_cards(df=kpi)
        return kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "VALOR ATUAL": "COTAÇÃO",
            "MIN. 52 SEMANAS": "COTAÇÃO MÍNIMA 1 ANO",
            "MÁX. 52 SEMANAS": "COTAÇÃO MÁXIMA 1 ANO",
            "VALORIZAÇÃO (12M)": "VALORIZAÇÃO DE COTAÇÃO 1 ANO",
            "MIN. MÊS": "COTAÇÃO MÍNIMA 1 MÊS", "TOTAL": "VALOR EM CAIXA",
            "MÁX. MÊS": "COTAÇÃO MÁXIMA 1 MÊS",
            "VALOR EM CAIXA": "VALOR EM CAIXA %",
            "Nº DE COTAS": "QUANTIDADE DE COTAS",
            "TIPO DA GESTÃO": "GESTÃO", "LIQUIDEZ MÉDIA DIÁRIA": "LIQUIDEZ",
            "ÚLTIMOS 12 MESES": "DIVIDENDOS PAGOS 1 ANO",
            "MÊS ATUAL": "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
            "VAL. PATRIMONIAL P/COTA": "VALOR PATRIMONIAL/COTA",
            "NOME PREGÃO": "NOME", "VALOR MERCADO": "VALOR DE MERCADO",
            "Nº DE COTISTAS": "QUANTIDADE DE COTISTAS",
            "DY CAGR(5 ANOS)": "CAGR DIVIDENDOS 5 ANOS",
            "VALOR CAGR(5 ANOS)": "CAGR 5 ANOS",
            "ÍNICIO DO FUNDO": "DATA DE CRIAÇÃO",
            "PATRIMÔNIO": "VALOR PATRIMONIAL",
            "RENDIM. MÉDIO (24M)": "RENDIMENTO MÉDIO 2 ANOS",
            "TAXAS ADMINISTRAÇÃO": "TAXA ADMINISTRATIVA"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the brazilian reits infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_company(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "NOME", "CNPJ", "DATA DE CRIAÇÃO", "ADMINISTRADOR",
               "GESTÃO", "TIPO ANBIMA", "SEGMENTO ANBIMA", "SEGMENTO",
               "PÚBLICO-ALVO", "PRAZO DE DURAÇÃO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        if "MANDATO" in df.columns:
            df["MANDATO"] = df["MANDATO"].str.replace("HÍBRIDOS", "HÍBRIDO")
        if "DATA DE CRIAÇÃO" in df.columns:
            df["DATA DE CRIAÇÃO"] = pd.to_datetime(df["DATA DE CRIAÇÃO"],
                                                   format="%d/%m/%Y",
                                                   errors="coerce").dt.date
            df["DATA DE CRIAÇÃO"] = df["DATA DE CRIAÇÃO"].astype(str)

        df = _string_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the brazilian reits prices infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df1 = _clean_cards(df1)
        df2 = self._parse_company(soup)
        df3 = self._parse_price(soup)
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO", "COTAÇÃO MÍNIMA 1 MÊS",
               "COTAÇÃO MÁXIMA 1 MÊS", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
               "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO 1 ANO", "DIVIDENDOS PAGOS 1 ANO",
               "RENDIMENTO MÉDIO 2 ANOS"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VALORIZAÇÃO DE COTAÇÃO 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO 1 MÊS"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS",
               "DIVIDENDOS PAGOS 1 ANO", "RENDIMENTO MÉDIO 2 ANOS"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self):
        """
        Summary.

        Function to retrieve the brazilian reits kpis infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df1 = _clean_cards(df1)
        df2 = self._parse_company(soup)
        df3 = self._parse_price(soup)
        df4 = self._parse_kpi(soup)
        df = pd.concat([df1, df2, df3, df4])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "VALOR DE MERCADO", "VALOR PATRIMONIAL",
               "P/VP", "LIQUIDEZ", "DIVIDEND YIELD", "VALOR PATRIMONIAL/COTA",
               "VALOR EM CAIXA", "VALOR EM CAIXA %", "CAGR 5 ANOS",
               "CAGR 3 ANOS", "CAGR DIVIDENDOS 5 ANOS",
               "CAGR DIVIDENDOS 3 ANOS", "QUANTIDADE DE COTAS",
               "QUANTIDADE DE COTISTAS", "TAXA ADMINISTRATIVA"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        if "DIVIDEND YIELD" in df.columns:
            df["DIVIDEND YIELD"] = df["DIVIDEND YIELD"].apply(
                lambda x: f"{x}%" if pd.notna(x) else x)
        if "VALOR EM CAIXA %" in df.columns:
            df["VALOR EM CAIXA %"] = df["VALOR EM CAIXA %"].apply(
                lambda x: f"{x}%" if pd.notna(x) else x)

        tmp = ["DIVIDEND YIELD", "VALOR EM CAIXA %", "TAXA ADMINISTRATIVA"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["LIQUIDEZ", "VALOR PATRIMONIAL/COTA",
               "P/VP", "VALOR EM CAIXA", "CAGR DIVIDENDOS 3 ANOS",
               "CAGR 3 ANOS", "QUANTIDADE DE COTISTAS", "VALOR PATRIMONIAL",
               "CAGR 5 ANOS", "VALOR DE MERCADO", "QUANTIDADE DE COTAS",
               "CAGR DIVIDENDOS 5 ANOS"]
        df = _numeric_columns(df=df, columns=tmp)
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

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS", "P/VP",
               "DIVIDENDOS PAGOS 1 ANO", "VALOR EM CAIXA", "LIQUIDEZ",
               "RENDIMENTO MÉDIO 2 ANOS", "VALOR PATRIMONIAL/COTA",
               "CAGR DIVIDENDOS 3 ANOS", "CAGR 3 ANOS", "VALOR DE MERCADO",
               "QUANTIDADE DE COTISTAS", "VALOR PATRIMONIAL", "CAGR 5 ANOS",
               "QUANTIDADE DE COTAS", "CAGR DIVIDENDOS 5 ANOS"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VALORIZAÇÃO DE COTAÇÃO 1 ANO", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
               "DIVIDEND YIELD", "VALOR EM CAIXA %", "TAXA ADMINISTRATIVA"]
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
        url = "https://statusinvest.com.br/etfs/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom):
        administrador = dom.xpath("/html/body/main/div[2]/div[1]/div[1]/" +
                                  "div[1]/div[2]/strong")
        administrador = (administrador[0].text.upper()
                         if administrador and administrador[0].text
                         else None)
        nome = dom.xpath("/html/body/main/div[2]/div[1]/h4/span")
        nome = (nome[0].text.upper().strip()
                if nome and nome[0].text else None)
        gestor = dom.xpath("/html/body/main/div[2]/div[1]/div[1]/div[1]/" +
                           "div[1]/strong")
        gestor = (gestor[0].text.upper().strip()
                  if gestor and gestor[0].text else None)
        indice = dom.xpath("/html/body/main/div[1]/div[3]/div/div/" +
                           "div[1]/div/div/div/strong/small")
        indice = (indice[0].text.upper().strip()
                  if indice and indice[0].text else None)
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        tmp.append({"INFO": "NOME", "VALOR": nome})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        tmp.append({"INFO": "ADMINISTRADOR", "VALOR": administrador})
        tmp.append({"INFO": "GESTOR", "VALOR": gestor})
        tmp.append({"INFO": "ÍNDICE", "VALOR": indice})
        df = pd.DataFrame(tmp)
        df = _clean_cards(df=df)
        return df

    def _parse_company(self, soup):
        # Company 1.
        cells = soup.find("div",
                          {"class": "card bg-main-gd-h white-text " +
                           "rounded mb-5"})
        cells = cells.find_all("div", {"class": "info pr-md-2"})
        tmp = []
        for cell in cells:
            title = cell.find("span", {"class": "sub-value"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title, "VALOR": value})
        df1 = pd.DataFrame(tmp)  # Temporary dataframe.

        # Company 2.
        cells = soup.find("div",
                          {"class": "top-info info-3 sm d-flex " +
                           "justify-between"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        for cell in cells:
            title = cell.find("h3", {"class": "title m-0"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title, "VALOR": value})
        df2 = pd.DataFrame(tmp)  # Temporary dataframe.
        company = pd.concat([df1, df2])
        company = _clean_cards(df=company)
        return company

    def _parse_price(self, soup):
        cells = soup.find("div",
                          {"class": "top-info mt-4 has-special d-flex " +
                           "justify-between flex-wrap"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        tmp2 = []
        tmp3 = []
        for cell in cells:  # Getting elements.
            title1 = cell.find("h3", {"class": "title"})
            title2 = cell.find("span", {"class": "title"})
            title3 = cell.find("span", {"class": "sub-title"})
            value1 = cell.find("strong", {"class": "value"})
            value2 = cell.find("strong", {"class": "value"})
            value3 = cell.find("span", {"class": "sub-value"})
            if title1 or title2 or title3:
                title1 = (title1.get_text(strip=True).upper()
                          if title1 else None)
                title2 = (title2.get_text(strip=True).upper()
                          if title2 else None)
                title3 = (title3.get_text(strip=True).upper()
                          if title3 else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                value3 = (value3.get_text(strip=True).upper()
                          if value3 else None)
                tmp.append({"INFO": title1, "VALOR": value1})
                tmp2.append({"INFO": title2, "VALOR": value1})
                tmp3.append({"INFO": title3, "VALOR": value3})
        price = pd.concat([pd.DataFrame(tmp), pd.DataFrame(tmp2),
                           pd.DataFrame(tmp3)])
        price.reset_index(drop=True, inplace=True)  # Reseting index.
        price = _clean_cards(df=price)
        return price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "Nº DE COTISTAS": "QUANTIDADE DE COTISTAS", "CÓDIGO ISIN": "ISIN",
            "DATA DE INÍCIO": "DATA DE CRIAÇÃO", "D.Y": "DIVIDEND YIELD",
            "LIQUIDEZ MÉDIA DIÁRIA": "LIQUIDEZ", "TIPO": "TIPO ATIVO",
            "SETOR DE ATUAÇÃO": "SETOR", "MÁX. MÊS": "COTAÇÃO MÁXIMA 1 MÊS",
            "MIN. MÊS": "COTAÇÃO MÍNIMA 1 MÊS",
            "SUBSETOR DE ATUAÇÃO": "SUBSETOR", "VALOR ATUAL": "COTAÇÃO",
            "TAXA DEADM.ADMINISTRAÇÃO": "TAXA ADMINISTRATIVA",
            "LOTE MÍNIMO(EMISSÃO/RESGATE)": "LOTE MÍNIMO",
            "MÊS ATUAL": "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
            "MIN. 52 SEMANAS": "COTAÇÃO MÍNIMA 1 ANO",
            "MÁX. 52 SEMANAS": "COTAÇÃO MÁXIMA 1 ANO",
            "VALORIZAÇÃO (12M)": "VALORIZAÇÃO DE COTAÇÃO 1 ANO",
            "ÚLTIMOS 12 MESES": "DIVIDENDOS PAGOS 1 ANO"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the brazilian ETFs infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_company(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "NOME", "CNPJ", "ISIN", "TIPO ATIVO",
               "DATA DE CRIAÇÃO", "ADMINISTRADOR", "GESTOR", "MERCADO",
               "ÍNDICE", "BOOKNAME"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        if "DATA DE CRIAÇÃO" in df.columns:
            df["DATA DE CRIAÇÃO"] = pd.to_datetime(df["DATA DE CRIAÇÃO"],
                                                   format="%d/%m/%Y",
                                                   errors="coerce").dt.date
            df["DATA DE CRIAÇÃO"] = df["DATA DE CRIAÇÃO"].astype(str)

        df = _string_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the brazilian ETFs prices infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_price(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO", "COTAÇÃO MÍNIMA 1 MÊS",
               "COTAÇÃO MÁXIMA 1 MÊS", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
               "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO 1 ANO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VALORIZAÇÃO DE COTAÇÃO 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO 1 MÊS"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS"]
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
        df1 = self._parse_common_data(dom)
        df2 = self._parse_company(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "PATRIMÔNIO LÍQUIDO", "LIQUIDEZ",
               "TOTAL EM CARTEIRA", "QUANTIDADE DE COTISTAS", "RATIO",
               "LOTE PADRÃO", "LOTE MÍNIMO", "TAXA ADMINISTRATIVA"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "TAXA ADMINISTRATIVA"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["PATRIMÔNIO LÍQUIDO", "TOTAL EM CARTEIRA", "LIQUIDEZ", "RATIO",
               "LOTE PADRÃO", "LOTE MÍNIMO", "QUANTIDADE DE COTISTAS"]
        df = _numeric_columns(df=df, columns=tmp)
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

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS", "LOTE PADRÃO",
               "PATRIMÔNIO LÍQUIDO", "LOTE MÍNIMO", "TOTAL EM CARTEIRA",
               "LIQUIDEZ", "RATIO", "QUANTIDADE DE COTISTAS"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VALORIZAÇÃO DE COTAÇÃO 1 ANO", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
               "TAXA ADMINISTRATIVA"]
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
            urls = "https://statusinvest.com.br/acoes/eua/{}"
            self.url = urls.format(ticket.lower())
        elif type_asset == "REITS":
            urlr = "https://statusinvest.com.br/reits/{}"
            self.url = urlr.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom):
        tipo_ativo = dom.xpath("/html/body/main/header/div[2]/div/" +
                               "div[1]/div[1]/span")
        tipo_ativo = (tipo_ativo[0].text.upper().strip()
                      if tipo_ativo and tipo_ativo[0].text else None)
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        tmp.append({"INFO": "TIPO ATIVO", "VALOR": tipo_ativo})
        tmp.append({"INFO": "MOEDA", "VALOR": "USD"})
        df = pd.DataFrame(tmp)
        df = _clean_cards(df=df)
        return df

    def _parse_company(self, soup):
        cells = soup.find("div",
                          {"class": "card rounded text-main-green-dark " +
                           "mb-5"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        for cell in cells:
            title = cell.find("span",
                              {"class": "sub-value legend-tooltip pr-2 " +
                               "d-inline-block"})
            value1 = cell.find("h2", {"class": "value"})
            value2 = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                tmp.append({"INFO": title, "VALOR": value1, "VALOR2": value2})
        df1 = pd.DataFrame(tmp)  # Temporary dataframe.
        df1["D"] = df1.apply(
            lambda row: row["VALOR"]
            if row["VALOR"] is not None else row["VALOR2"], axis=1)
        df1 = df1[["INFO", "D"]]  # Necessary columns.
        df1 = df1.rename(columns={"D": "VALOR"})  # Renaming columns.

        # Company 2.
        cells = soup.find("div",
                          {"class": "card bg-main-gd-h white-text " +
                           "rounded"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        for cell in cells:
            title = cell.find("span", {"class": "sub-value"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title, "VALOR": value})
        df2 = pd.DataFrame(tmp)  # Temporary dataframe.

        # Company 3.
        cells = soup.find("div",
                          {"class": "top-info info-3 sm d-flex justify-" +
                           "between mb-5"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        for cell in cells:
            title = cell.find("h3", {"class": "title m-0"})
            value = cell.find("strong", {"class": "value"})
            if title:
                title = (title.get_text(strip=True).upper()
                         if title else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title, "VALOR": value})
        df3 = pd.DataFrame(tmp)  # Temporary dataframe.
        df3.at[0, "INFO"] = "PATRIMÔNIO LÍQUIDO"  # Raneming cell.
        company = pd.concat([df1, df2, df3])
        company = _clean_cards(df=company)
        return company

    def _parse_price(self, soup):
        cells = soup.find("div",
                          {"class": "top-info has-special d-flex justify-" +
                           "between flex-wrap"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        tmp2 = []
        tmp3 = []
        for cell in cells:  # Getting elements.
            title1 = cell.find("h3", {"class": "title"})
            title2 = cell.find("span", {"class": "title"})
            title3 = cell.find("span", {"class": "sub-title"})
            value1 = cell.find("strong", {"class": "value"})
            value2 = cell.find("strong", {"class": "value"})
            value3 = cell.find("span", {"class": "sub-value"})
            if title1 or title2 or title3:
                title1 = (title1.get_text(strip=True).upper()
                          if title1 else None)
                title2 = (title2.get_text(strip=True).upper()
                          if title2 else None)
                title3 = (title3.get_text(strip=True).upper()
                          if title3 else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                value3 = (value3.get_text(strip=True).upper()
                          if value3 else None)
                tmp.append({"INFO": title1, "VALOR": value1})
                tmp2.append({"INFO": title2, "VALOR": value1})
                tmp3.append({"INFO": title3, "VALOR": value3})
        price = pd.concat([pd.DataFrame(tmp), pd.DataFrame(tmp2),
                           pd.DataFrame(tmp3)])
        price.reset_index(drop=True, inplace=True)  # Reseting index.
        price = price.drop([3])  # Removing unnecessary rows.
        price = _clean_cards(df=price)
        return price

    def _parse_kpi(self, soup):
        cells = soup.find("div", {"class": "d-flex flex-wrap"})
        cells2 = cells.find_all("div",
                                {"class": "w-50 w-sm-33 w-md-25 " +
                                 "w-lg-16_6 mb-2 mt-2 item"}) + \
            cells.find_all("div",
                           {"class": "w-50 w-sm-33 w-md-25 w-lg-50 " +
                            "mb-2 mt-2 item"})
        tmp = []
        for cell in cells2:
            title1 = cell.find("h3", {"class": "title m-0 uppercase"})
            title2 = cell.find("h3", {"class": "title m-0 mr-1 uppercase"})
            value = cell.find("strong", {"class": "value"})
            if title1 or title2:
                title1 = (title1.get_text(strip=True).upper()
                          if title1 else None)
                title2 = (title2.get_text(strip=True).upper()
                          if title2 else None)
                value = (value.get_text(strip=True).upper()
                         if value else None)
                tmp.append({"INFO": title1, "VALOR": title2, "VALOR2": value})
        kpi = pd.DataFrame(tmp)  # Temporary dataframe.
        kpi["INFO"] = kpi.apply(
            lambda row: row["INFO"]
            if row["INFO"] is not None else row["VALOR"], axis=1)
        kpi = kpi[["INFO", "VALOR2"]]  # Necessary columns.
        kpi = kpi.rename(columns={"VALOR2": "VALOR"})  # Renaming columns.
        kpi = _clean_cards(df=kpi)
        return kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "BOOKNAME": "EMPRESA", "SETOR": "SETOR EUA",
            "SETOR DE ATUAÇÃO": "SETOR", "M. LÍQUIDA": "MARGEM LÍQUIDA",
            "SUBSETOR DE ATUAÇÃO": "SUBSETOR", "ATIVOS": "ATIVOS USD",
            "SEGMENTO DE ATUAÇÃO": "SEGMENTO", "D.Y": "DIVIDEND YIELD",
            "PATRIMÔNIO LÍQUIDO": "PATRIMÔNIO LÍQUIDO USD",
            "ATIVO CIRCULANTE": "ATIVO CIRCULANTE USD",
            "DÍVIDA BRUTA": "DÍVIDA BRUTA USD", "M. EBITDA": "MARGEM EBITDA",
            "DISPONIBILIDADE": "DISPONIBILIDADE USD",
            "DÍVIDA LÍQUIDA": "DÍVIDA LÍQUIDA USD",
            "VALOR DE MERCADO": "VALOR DE MERCADO USD",
            "VALOR DE FIRMA": "VALOR DE FIRMA USD",
            "VALOR ATUAL": "COTAÇÃO USD", "P/SR": "P/RECEITA LÍQUIDA",
            "MIN. 52 SEMANAS": "COTAÇÃO MÍNIMA USD 1 ANO",
            "MIN. MÊS": "COTAÇÃO MÍNIMA USD 1 MÊS",
            "MÁX. 52 SEMANAS": "COTAÇÃO MÁXIMA USD 1 ANO",
            "MÁX. MÊS": "COTAÇÃO MÁXIMA USD 1 MÊS",
            "ÚLTIMOS 12 MESES": "DIVIDENDOS PAGOS USD 1 ANO",
            "VALORIZAÇÃO (12M)": "VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
            "MÊS ATUAL": "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS",
            "M. BRUTA": "MARGEM BRUTA", "M. EBIT": "MARGEM EBIT",
            "P/CAP. GIRO": "P/CAPITAL DE GIRO", "MERCADO DE ORIGEM": "MERCADO",
            "LIQ. CORRENTE": "LIQUIDEZ CORRENTE", "INDÚSTRIA": "SUBSETOR EUA",
            "P/ATIVO CIRC. LIQ.": "P/ATIVO CIRCULANTE LÍQUIDO",
            "DÍV. LÍQUIDA/PL": "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO",
            "DÍV. LÍQUIDA/EBITDA": "DÍVIDA LÍQUIDA/EBITDA",
            "DÍV. LÍQUIDA/EBIT": "DÍVIDA LÍQUIDA/EBIT",
            "PL/ATIVOS": "PATRIMÔNIO LÍQUIDO/ATIVOS"}
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
        tmp = ["TICKET", "EMPRESA", "TIPO ATIVO", "MERCADO", "SETOR EUA",
               "SUBSETOR EUA", "SETOR", "SUBSETOR", "SEGMENTO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        df = _string_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the stocks and reits prices infos.
        ticket: String. Ticket code.
        type_asset: String. "STOCK" or "REIT".
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_price(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO USD", "COTAÇÃO MÍNIMA USD 1 MÊS",
               "COTAÇÃO MÁXIMA USD 1 MÊS", "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS",
               "COTAÇÃO MÍNIMA USD 1 ANO", "COTAÇÃO MÁXIMA USD 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
               "DIVIDENDOS PAGOS USD 1 ANO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO USD", "COTAÇÃO MÍNIMA USD 1 ANO",
               "COTAÇÃO MÁXIMA USD 1 ANO", "COTAÇÃO MÍNIMA USD 1 MÊS",
               "COTAÇÃO MÁXIMA USD 1 MÊS", "DIVIDENDOS PAGOS USD 1 ANO"]
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
        tmp = ["TICKET", "MOEDA", "PATRIMÔNIO LÍQUIDO USD",
               "VALOR DE MERCADO USD", "DÍVIDA LÍQUIDA USD",
               "DÍVIDA LÍQUIDA/EBITDA", "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO",
               "ROE", "ROA", "ROIC", "MARGEM LÍQUIDA", "MARGEM EBITDA",
               "MARGEM EBIT", "CAGR LUCROS 5 ANOS", "CAGR RECEITAS 5 ANOS",
               "P/L", "P/VP", "EV/EBITDA", "EV/EBIT", "P/EBITDA", "P/EBIT",
               "P/RECEITA LÍQUIDA", "LIQUIDEZ CORRENTE", "PASSIVOS/ATIVOS",
               "ATIVOS USD", "ATIVO CIRCULANTE USD", "DISPONIBILIDADE USD",
               "DÍVIDA BRUTA USD", "DIVIDEND YIELD", "VPA", "P/ATIVO",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO",
               "GIRO ATIVOS", "MARGEM BRUTA", "LPA", "PEG RATIO",
               "DÍVIDA LÍQUIDA/EBIT", "PATRIMÔNIO LÍQUIDO/ATIVOS",
               "VALOR DE FIRMA USD"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["DIVIDEND YIELD", "ROE", "ROA", "ROIC", "MARGEM BRUTA",
               "MARGEM EBITDA", "MARGEM EBIT", "MARGEM LÍQUIDA", "MOEDA",
               "CAGR RECEITAS 5 ANOS", "CAGR LUCROS 5 ANOS", "TICKET"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["PATRIMÔNIO LÍQUIDO USD", "ATIVOS USD", "ATIVO CIRCULANTE USD",
               "DÍVIDA BRUTA USD", "DISPONIBILIDADE USD", "DÍVIDA LÍQUIDA USD",
               "VALOR DE MERCADO USD", "VALOR DE FIRMA USD", "GIRO ATIVOS",
               "P/L", "PEG RATIO", "P/VP", "EV/EBITDA", "EV/EBIT", "P/EBITDA",
               "P/EBIT", "VPA", "P/ATIVO", "LPA", "P/RECEITA LÍQUIDA",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "DÍVIDA LÍQUIDA/EBITDA",
               "DÍVIDA LÍQUIDA/EBIT", "PATRIMÔNIO LÍQUIDO/ATIVOS",
               "PASSIVOS/ATIVOS", "LIQUIDEZ CORRENTE"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self):
        """
        Summary.

        Function to aggregate the stocks and reits full infos.
        ticket: String. Ticket code.
        """
        df = pd.concat([self.info(), self.price(), self.kpi()])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        df = df.drop(["INFO"], axis=1, errors="ignore")  # Necessary rows.

        tmp = ["COTAÇÃO USD", "COTAÇÃO MÍNIMA USD 1 ANO", "LIQUIDEZ CORRENTE",
               "COTAÇÃO MÁXIMA USD 1 ANO", "COTAÇÃO MÍNIMA USD 1 MÊS",
               "COTAÇÃO MÁXIMA USD 1 MÊS", "DIVIDENDOS PAGOS USD 1 ANO",
               "PATRIMÔNIO LÍQUIDO USD", "ATIVOS USD", "ATIVO CIRCULANTE USD",
               "DÍVIDA BRUTA USD", "DISPONIBILIDADE USD", "DÍVIDA LÍQUIDA USD",
               "VALOR DE MERCADO USD", "VALOR DE FIRMA USD", "GIRO ATIVOS",
               "P/L", "PEG RATIO", "P/VP", "EV/EBITDA", "EV/EBIT", "P/EBITDA",
               "P/EBIT", "VPA", "P/ATIVO", "LPA", "P/RECEITA LÍQUIDA",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "DÍVIDA LÍQUIDA/EBITDA",
               "DÍVIDA LÍQUIDA/EBIT", "PATRIMÔNIO LÍQUIDO/ATIVOS",
               "PASSIVOS/ATIVOS"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VALORIZAÇÃO DE COTAÇÃO USD 1 ANO", "CAGR LUCROS 5 ANOS",
               "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS", "CAGR RECEITAS 5 ANOS",
               "DIVIDEND YIELD", "ROE", "ROA", "ROIC", "MARGEM BRUTA",
               "MARGEM EBITDA", "MARGEM EBIT", "MARGEM LÍQUIDA"]
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
        url = "https://statusinvest.com.br/etf/eua/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom):
        nome = dom.xpath("/html/body/main/header/div[2]/div/div[1]/h1/" +
                         "small")
        nome = (nome[0].text.upper().strip()
                if nome and nome[0].text else None).split("-")[0]
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": self.ticket.strip().upper()})
        tmp.append({"INFO": "NOME", "VALOR": nome})
        tmp.append({"INFO": "MOEDA", "VALOR": "USD"})
        df = pd.DataFrame(tmp)
        df = _clean_cards(df=df)
        return df

    def _parse_price(self, soup):
        cells = soup.find("div",
                          {"class": "top-info has-special d-flex " +
                           "justify-between flex-wrap"})
        cells = cells.find_all("div", {"class": "info"})
        tmp = []
        tmp2 = []
        tmp3 = []
        for cell in cells:  # Getting elements.
            title1 = cell.find("h3", {"class": "title"})
            title2 = cell.find("span", {"class": "title"})
            title3 = cell.find("span", {"class": "sub-title"})
            value1 = cell.find("strong", {"class": "value"})
            value2 = cell.find("strong", {"class": "value"})
            value3 = cell.find("span", {"class": "sub-value"})
            if title1 or title2 or title3:
                title1 = (title1.get_text(strip=True).upper()
                          if title1 else None)
                title2 = (title2.get_text(strip=True).upper()
                          if title2 else None)
                title3 = (title3.get_text(strip=True).upper()
                          if title3 else None)
                value1 = (value1.get_text(strip=True).upper()
                          if value1 else None)
                value2 = (value2.get_text(strip=True).upper()
                          if value2 else None)
                value3 = (value3.get_text(strip=True).upper()
                          if value3 else None)
                tmp.append({"INFO": title1, "VALOR": value1})
                tmp2.append({"INFO": title2, "VALOR": value1})
                tmp3.append({"INFO": title3, "VALOR": value3})
        price = pd.concat([pd.DataFrame(tmp), pd.DataFrame(tmp2),
                           pd.DataFrame(tmp3)])
        price.reset_index(drop=True, inplace=True)  # Reseting index.
        price = _clean_cards(df=price)
        return price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        column_mapping = {
            "VALOR ATUAL": "COTAÇÃO USD",
            "MÊS ATUAL": "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS",
            "MÁX. MÊS": "COTAÇÃO MÁXIMA USD 1 MÊS",
            "MIN. 52 SEMANAS": "COTAÇÃO MÍNIMA USD 1 ANO",
            "MÁX. 52 SEMANAS": "COTAÇÃO MÁXIMA USD 1 ANO",
            "VALORIZAÇÃO (12M)": "VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
            "ÚLTIMOS 12 MESES": "DIVIDENDOS PAGOS USD 1 ANO",
            "MIN. MÊS": "COTAÇÃO MÍNIMA USD 1 MÊS"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self):
        """
        Summary.

        Function to retrieve the ETFs infos.

        """
        dom = self._get_soup()[1]
        df = self._parse_common_data(dom)
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "NOME"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        df = _string_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self):
        """
        Summary.

        Function to retrieve the ETFs prices infos.
        """
        soup, dom = self._get_soup()
        df1 = self._parse_common_data(dom)
        df2 = self._parse_price(soup)
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        # Necessary columns.
        tmp = ["TICKET", "MOEDA", "COTAÇÃO USD", "COTAÇÃO MÍNIMA USD 1 MÊS",
               "COTAÇÃO MÁXIMA USD 1 MÊS", "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS",
               "COTAÇÃO MÍNIMA USD 1 ANO", "COTAÇÃO MÁXIMA USD 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
               "DIVIDENDOS PAGOS USD 1 ANO"]
        df = df.loc[:, [col for col in tmp if col in df.columns]]

        tmp = ["TICKET", "MOEDA", "VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS"]
        df = _string_columns(df=df, columns=tmp)

        tmp = ["COTAÇÃO USD", "COTAÇÃO MÍNIMA USD 1 ANO",
               "COTAÇÃO MÁXIMA USD 1 ANO", "COTAÇÃO MÍNIMA USD 1 MÊS",
               "COTAÇÃO MÁXIMA USD 1 MÊS"]
        df = _numeric_columns(df=df, columns=tmp)
        df = df.T.reset_index(drop=False)
        # df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self):
        """
        Summary.

        Function to aggregate the ETFs full infos.
        """
        df = pd.concat([self.info(), self.price()])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing first row.
        df = df.drop(["INFO"], axis=1, errors="ignore")  # Necessary rows.

        tmp = ["COTAÇÃO USD", "COTAÇÃO MÍNIMA USD 1 ANO",
               "COTAÇÃO MÁXIMA USD 1 ANO", "COTAÇÃO MÍNIMA USD 1 MÊS",
               "COTAÇÃO MÁXIMA USD 1 MÊS"]
        for column in tmp:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        tmp = ["VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS",]
        for column in tmp:
            if column in df.columns:
                df[column] = df[column].str.replace("%", "", regex=False)
                df[column] = pd.to_numeric(df[column], errors="coerce")
        return df
