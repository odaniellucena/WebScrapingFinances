"""
Summary.

Retrieve the companies infos from Investidor 10 website.
"""
# -*- coding: utf-8 -*-

import Auxiliaries as aux
from bs4 import BeautifulSoup
from lxml import etree
import requests
import pandas as pd

# Header to use to get the web page content in text format.
"""
The User-Agent request header contains a characteristic string that allows the
network protocol peers to identify the application type, operating system,
software vendor or software version of the requesting software user agent.
Validating User-Agent header on server side is a common operation so be sure to
use valid browser’s User-Agent string to avoid getting blocked.
Font: https://go-colly.org/articles/scraping_related_http_headers/
Font: https://stackoverflow.com/questions/68259148/getting-404-error-for-
      certain-stocks-and-pages-on-yahoo-finance-python
"""
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


def assets_auxtable(type_asset):
    """
    Summary.

    Retrieve the auxiliar table for stocks.
    type_asset: String. ACAO, FII, STOCK, REIT.
    """
    if type_asset == "ACAO":
        url_format = ("https://investidor10.com.br/acoes/?page={}")
        p = 9  # Pages on website.
    elif type_asset == "FII":
        url_format = ("https://investidor10.com.br/fiis/?page={}")
        p = 14  # Pages on website.
    elif type_asset == "STOCK":
        url_format = ("https://investidor10.com.br/stocks/?page={}")
        p = 127  # Pages on website.
    else:
        url_format = ("https://investidor10.com.br/reits/?page={}")
        p = 5  # Pages on website.

    urls = [url_format.format(page) for page in range(1, p + 1)]
    df = []
    for url in urls:
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        # Checking if page exist.
        if page.status_code != 200:
            continue
            # raise ValueError("Page does not exist")

        tmp = []
        link = ([a["href"].split("/")[-2].upper()
                 for a in soup.select(".actions-card a")])
        title = ([h3.get_text(strip=True).upper()
                  for h3 in soup.select(".actions-title")])
        tmp = {"TICKET": link, "EMPRESA": title}
        df.append(pd.DataFrame(tmp))
    df = pd.concat(df, ignore_index=True)  # Definitive dataframe.
    return df


def etfbr_auxtable():
    """
    Summary.

    Retrieve the auxiliar table for brazilian ETFs.
    """
    url_format = ("https://investidor10.com.br/etfs/?order=ticker&" +
                  "dir=asc&page={}")  # URL.
    p = 5  # Pages on website.
    urls = [url_format.format(page) for page in range(1, p + 1)]
    df = []  # Definitive list.
    for url in urls:
        page = requests.get(url, headers=headers)
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
                    i = column[0].text.strip().upper()
                    nome = column[1].text.strip().upper()
                    ativo = column[2].text.strip().upper()
                    cotacao = column[3].text.strip().upper()
                    volume = column[4].text.strip().upper()
                    var_30d = column[5].text.strip().upper()
                    var_12m = column[6].text.strip().upper()
                    tmp.append({"ID": i, "NOME": nome, "ATIVO": ativo,
                                "COTAÇÃO": cotacao, "VOLUME": volume,
                                "VARIAÇÃO DE COTAÇÃO 1 MÊS": var_30d,
                                "VARIAÇÃO DE COTAÇÃO 1 ANO": var_12m})
            df.append(pd.DataFrame(tmp))

    df = pd.concat(df, ignore_index=True)  # Definitive dataframe.
    df.drop(["ID"], axis=1, inplace=True)  # Removing column.
    df["COTAÇÃO"] = pd.to_numeric(df["COTAÇÃO"], errors="coerce")
    df["VOLUME"] = pd.to_numeric(df["VOLUME"], errors="coerce")
    df["LIQUIDEZ"] = df["VOLUME"]*df["COTAÇÃO"]

    tmp = ["VARIAÇÃO DE COTAÇÃO 1 MÊS", "VARIAÇÃO DE COTAÇÃO 1 ANO"]
    for column in tmp:
        if column in df.columns:
            df[column] = df[column].replace({"-": None, "": None, "0": None})
            df[column] = pd.to_numeric(df[column], errors="coerce")
            df[column] = round(df[column], 2)
            df[column] = df[column].apply(lambda x: f"{x}%"
                                          if pd.notna(x) else x)

    tmp = ["NOME", "ATIVO"]
    df = aux.string_columns(df, tmp)
    df.to_parquet("INVESTIDOR10_ETFSBR.parquet")
    return df


def etf_auxtable():
    """
    Summary.

    Retrieve the auxiliar table for ETFs.
    """
    url_format = ("https://investidor10.com.br/etfs-global/?" +
                  "order=ticker&dir=asc&page={}")  # URL.
    p = 95  # Pages on website.
    urls = [url_format.format(page) for page in range(1, p + 1)]
    df = []  # Definitive list.
    for url in urls:
        page = requests.get(url, headers=headers)
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
                    i = column[0].text.strip().upper()
                    nome = column[1].text.strip().upper()
                    ativo = column[2].text.strip().upper()
                    cotacao_usd = column[3].text.strip().upper()
                    cotacao_brl = column[4].text.strip().upper()
                    # val_mercado = column[5].text.strip().upper()
                    volume_usd = column[6].text.strip().upper()
                    var_30d = column[7].text.strip().upper()
                    var_12m = column[8].text.strip().upper()
                    tmp.append({"ID": i, "NOME": nome, "ATIVO": ativo,
                                "VARIAÇÃO DE COTAÇÃO USD 1 ANO": var_12m,
                                "COTAÇÃO USD": cotacao_usd,
                                "COTAÇÃO BRL": cotacao_brl,
                                # "VALOR DE MERCADO USD": val_mercado,
                                "VOLUME USD": volume_usd,
                                "VARIAÇÃO DE COTAÇÃO USD 1 MÊS": var_30d})
            df.append(pd.DataFrame(tmp))

    df = pd.concat(df, ignore_index=True)  # Definitive dataframe.
    df.drop(["ID"], axis=1, inplace=True)  # Removing column.

    tmp = ["COTAÇÃO USD", "COTAÇÃO BRL", "VALOR DE MERCADO USD", "VOLUME USD"]
    df = aux.numeric_columns(df, tmp)
    df["LIQUIDEZ USD"] = df["VOLUME USD"]*df["COTAÇÃO USD"]

    tmp = ["VARIAÇÃO DE COTAÇÃO USD 1 MÊS", "VARIAÇÃO DE COTAÇÃO USD 1 ANO"]
    for column in tmp:
        if column in df.columns:
            df[column] = df[column].replace({"-": None, "": None, "0": None})
            df[column] = pd.to_numeric(df[column], errors="coerce")
            df[column] = round(df[column], 2)
            df[column] = df[column].apply(lambda x: f"{x}%"
                                          if pd.notna(x) else x)

    tmp = ["NOME", "ATIVO"]
    df = aux.string_columns(df, tmp)
    df.to_parquet("INVESTIDOR10_ETFS.parquet")
    return df


class StocksBR:
    """
    Summary.

    Retrieve the brazilian stocks companies infos.
    """

    def __init__(self):
        self.url = "https://investidor10.com.br/acoes/{}"

    def _get_soup(self, ticket):
        url = self.url.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200:
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, ticket):
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        df = pd.DataFrame(tmp)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
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
                tmp.append({"INFO": title, "VALOR": value1, "VALOR2": value2})
        df2 = pd.DataFrame(tmp)  # Temporary dataframe.
        df2["VALOR"] = df2.apply(
            lambda row: row["VALOR"]
            if row["VALOR"] is not None else row["VALOR2"], axis=1)
        df2 = df2[["INFO", "VALOR"]]  # Necessary columns.
        company = pd.concat([df1, df2])
        company = aux.clean_cards(company)

        # Price.
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
        price = price.drop([2, 3, 4])  # Removing unnecessary row if any.
        price = aux.clean_cards(price)

        # KPI.
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
        kpi = aux.clean_cards(kpi)
        return company, price, kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
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

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian stocks infos.
        ticket: String. Ticket code.
        """
        soup = self._get_soup(ticket)[0]
        df1 = self._parse_common_data(ticket)
        df1 = df1.drop([1])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        # Necessary rows.
        df2 = df2.drop([5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17])
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["QUANTIDADE DE FUNCIONÁRIOS"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["EMPRESA", "CNPJ", "ANO IPO", "ANO FUNDAÇÃO", "SETOR",
               "SEGMENTO", "SEGMENTO DE MERCADO"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian stocks prices infos.
        ticket: String. Ticket code.
        """
        soup = self._get_soup(ticket)[0]
        df1 = self._parse_common_data(ticket)
        df1 = aux.clean_cards(df1)
        df2 = self._parse_cards(soup)[1]  # Price.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VARIAÇÃO DE COTAÇÃO 1 ANO"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian stocks kpi's infos.
        ticket: String. Ticket code.
        """
        soup = self._get_soup(ticket)[0]
        df1 = self._parse_common_data(ticket)
        df1 = aux.clean_cards(df1)
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([0, 1, 2, 3, 4, 14, 18, 19])  # Necessary rows.
        df3 = self._parse_cards(soup)[2]  # KPI.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)

        tmp = ["VALOR DE MERCADO", "VALOR DE FIRMA", "PATRIMÔNIO LÍQUIDO",
               "QUANTIDADE DE PAPÉIS", "ATIVOS", "ATIVO CIRCULANTE",
               "DÍVIDA BRUTA", "DÍVIDA LÍQUIDA", "DISPONIBILIDADE", "LIQUIDEZ",
               "P/L", "P/VP", "MARGEM LÍQUIDA", "MARGEM BRUTA", "MARGEM EBIT",
               "MARGEM EBITDA", "EV/EBIT", "P/EBIT", "P/ATIVO", "GIRO ATIVOS",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO", "VPA", "LPA",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "PASSIVOS/ATIVOS",
               "DÍVIDA BRUTA/PATRIMÔNIO LÍQUIDO", "LIQUIDEZ CORRENTE",
               "PATRIMÔNIO LÍQUIDO/ATIVOS", "DÍVIDA LÍQUIDA/EBIT"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["FREE FLOAT", "TAG ALONG", "DIVIDEND YIELD", "PAYOUT", "ROA",
               "ROE", "ROIC", "CAGR LUCROS 5 ANOS"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self, ticket):
        """
        Summary.

        Function to aggregate the brazilian stocks full infos.
        ticket: String. Ticket code.
        """
        df = pd.concat([self.info(ticket), self.price(ticket),
                        self.kpi(ticket)])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        df = df.drop(["INFO"], axis=1)
        return df


class ReitsBR:
    """
    Summary.

    Retrieve the brazilian reits companies infos.
    """

    def __init__(self):
        self.url = "https://investidor10.com.br/fiis/{}"

    def _get_soup(self, ticket):
        url = self.url.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200:
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, ticket):
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        df = pd.DataFrame(tmp)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
        # Company.
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
        # company = company.drop([14])  # Necessary rows.
        company = aux.clean_cards(company)

        # Price.
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
        price = aux.clean_cards(price)
        return company, price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        column_mapping = {
            "RAZÃO SOCIAL": "NOME", "LIQUIDEZ DIÁRIA": "LIQUIDEZ",
            "TIPO DE FUNDO": "SETOR", "TIPO DE GESTÃO": "GESTÃO",
            "COTAS EMITIDAS": "QUANTIDADE DE COTAS",
            "TAXA DE ADMINISTRAÇÃO": "TAXA ADMINISTRATIVA",
            "NUMERO DE COTISTAS": "QUANTIDADE DE COTISTAS",
            "VAL. PATRIMONIAL P/ COTA": "VALOR PATRIMONIAL/COTA",
            "VARIAÇÃO (12M)": "VARIAÇÃO DE COTAÇÃO 1 ANO"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian reits infos.
        ticket: String. Ticket code.
        """
        soup = self._get_soup(ticket)[0]
        df1 = self._parse_common_data(ticket)
        df1 = df1.drop([1])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([9, 10, 11, 12, 13, 14])  # Necessary rows.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["NOME", "CNPJ", "PÚBLICO-ALVO", "MANDATO", "SEGMENTO", "SETOR",
               "PRAZO DE DURAÇÃO", "GESTÃO", "TAXA ADMINISTRATIVA"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian reits prices infos.
        ticket: String. Ticket code.
        """
        soup = self._get_soup(ticket)[0]
        df1 = self._parse_common_data(ticket)
        df1 = aux.clean_cards(df1)
        df2 = self._parse_cards(soup)[1]  # Price.
        df2 = df2.drop([1, 2, 3])  # Necessary rows.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VARIAÇÃO DE COTAÇÃO 1 ANO"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian reits kpi's infos.
        ticket: String. Ticket code.
        """
        soup = self._get_soup(ticket)[0]
        df1 = self._parse_common_data(ticket)
        df1 = aux.clean_cards(df1)
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([0, 1, 2, 3, 4, 5, 6, 7, 8])  # Necessary rows.
        df3 = self._parse_cards(soup)[1]  # Price.
        df3 = df3.drop([0, 4])  # Necessary rows.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)

        tmp = ["QUANTIDADE DE COTISTAS", "QUANTIDADE DE COTAS", "P/VP",
               "VALOR PATRIMONIAL/COTA"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VALOR PATRIMONIAL", "LIQUIDEZ"]
        for column in tmp:
            if column in df.columns:
                df[column] = (df[column].str.replace("R$ ", "", regex=False)
                              .str.replace(".", "", regex=False)
                              .str.replace(",", ".", regex=False))

        df["VALOR PATRIMONIAL"] = df["VALOR PATRIMONIAL"].apply(aux.times)
        df["LIQUIDEZ"] = df["LIQUIDEZ"].apply(aux.times2)
        tmp = ["VACÂNCIA", "DIVIDEND YIELD"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self, ticket):
        """
        Summary.

        Function to aggregate the brazilian reits full infos.
        ticket: String. Ticket code.
        """
        df = pd.concat([self.info(ticket), self.price(ticket),
                        self.kpi(ticket)])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        df = df.drop(["INFO"], axis=1)
        return df


class ETFsBR:
    """
    Summary.

    Retrieve the brazilian ETF's companies infos.
    """

    def __init__(self):
        self.url = "https://investidor10.com.br/etfs/{}"
        self.aux = pd.read_parquet("INVESTIDOR10_ETFSBR.parquet")

    def _get_soup(self, ticket):
        url = self.url.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200:
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, soup, dom, ticket):
        nome = dom.xpath("/html/body/div[4]/main/header/div[2]/div/" +
                         "div[1]/div[2]/h2")
        nome = (nome[0].text.upper().strip()
                if nome and nome[0].text else None)
        infos = []
        infos.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        infos.append({"INFO": "NOME", "VALOR": nome})
        infos.append({"INFO": "MOEDA", "VALOR": "BRL"})
        df = pd.DataFrame(infos)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
        # Price.
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
        price = aux.clean_cards(price)
        return price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        column_mapping = {
            "DY": "DIVIDEND YIELD", "CAPITALIZAÇÃO": "VALOR DE MERCADO",
            "VARIAÇÃO (12M)": "VARIAÇÃO DE COTAÇÃO 1 ANO",
            "VARIAÇÃO (60N)": "VARIAÇÃO DE COTAÇÃO 5 ANOS"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian ETF's infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df = self._parse_common_data(soup, dom, ticket)
        df = df.drop([2])  # Necessary rows.
        return df

    def price(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian ETF's prices infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df1 = self.aux
        df1 = df1[df1["ATIVO"] == ticket.strip().upper()]
        df1 = df1[["VARIAÇÃO DE COTAÇÃO 1 MÊS"]]
        df1 = df1.reset_index(drop=True)
        df1 = df1.T.reset_index(drop=False)
        df1 = df1.rename(columns={"index": "INFO", 0: "VALOR"})
        df2 = self._parse_common_data(soup, dom, ticket)
        df2 = df2.drop([1])  # Necessary rows.
        df3 = self._parse_cards(soup)  # Price.
        df3 = df3.drop([1, 4])  # Necessary rows.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        tmp = ["COTAÇÃO"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VARIAÇÃO DE COTAÇÃO 1 ANO", "VARIAÇÃO DE COTAÇÃO 5 ANOS"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian ETF's kpi's infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df1 = self.aux
        df1 = df1[df1["ATIVO"] == ticket.strip().upper()]
        df1 = df1[["VOLUME", "LIQUIDEZ"]]
        df1 = df1.reset_index(drop=True)
        df1 = df1.T.reset_index(drop=False)
        df1 = df1.rename(columns={"index": "INFO", 0: "VALOR"})
        df2 = self._parse_common_data(soup, dom, ticket)
        df2 = df2.drop([1])  # Necessary rows.
        df3 = self._parse_cards(soup)  # Price.
        df3 = df3.drop([0, 2, 3])  # Necessary rows.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)

        tmp = ["DIVIDEND YIELD"]
        df = aux.string_columns(df, tmp)
        df["VALOR DE MERCADO"] = (df["VALOR DE MERCADO"]
                                  .str.replace("R$\n", "", regex=False))
        df["VALOR DE MERCADO"] = df["VALOR DE MERCADO"].apply(aux.times2)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self, ticket):
        """
        Summary.

        Function to aggregate the brazilian ETF's full infos.
        ticket: String. Ticket code.
        """
        df = pd.concat([self.info(ticket), self.price(ticket),
                        self.kpi(ticket)])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        df = df.drop(["INFO"], axis=1)
        return df


class StocksReits:
    """
    Summary.

    Retrieve the stocks and reits companies infos.
    """

    def __init__(self):
        self.urls = "https://investidor10.com.br/stocks/{}"
        self.urlr = "https://investidor10.com.br/reits/{}"

    def _get_soup(self, ticket, type_asset):
        if type_asset == "STOCK":
            url = self.urls.format(ticket.lower())
        else:
            url = self.urlr.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200:
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, soup, dom, ticket):
        empresa = dom.xpath("/html/body/div[4]/main/header/div[2]/div/" +
                            "div[1]/div[2]/h2")
        empresa = (empresa[0].text.upper().strip()
                   if empresa and empresa[0].text else None)
        cotacao_brl = dom.xpath("/html/body/div[4]/main/section/div/" +
                                "section[1]/div[1]/div[2]/div/span[2]")
        cotacao_brl = (cotacao_brl[0].text.upper().strip()
                       if cotacao_brl and cotacao_brl[0].text else None)
        infos = []
        infos.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        # infos.append({"INFO": "EMPRESA", "VALOR": empresa})
        infos.append({"INFO": "MOEDA", "VALOR": "USD"})
        infos.append({"INFO": "COTAÇÃO BRL", "VALOR": cotacao_brl})
        df = pd.DataFrame(infos)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
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
        company = aux.clean_cards(company)

        # Price.
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
        price = price.drop([2, 3, 4])  # Removing unnecessary row if any.
        price = aux.clean_cards(price)

        # KPIs
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
        kpi = aux.clean_cards(kpi)
        return company, price, kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
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

    def info(self, ticket, type_asset):
        """
        Summary.

        Function to retrieve the stocks and reits infos.
        ticket: String. Ticket code.
        type_asset: String. "STOCK" or "REIT".
        """
        soup, dom = self._get_soup(ticket, type_asset)
        df1 = self._parse_common_data(soup, dom, ticket)
        df1 = df1.drop([1, 2])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([6, 7, 8, 9, 10])  # Necessary rows.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["QUANTIDADE DE FUNCIONÁRIOS"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["EMPRESA", "PAÍS", "ANO IPO", "ANO FUNDAÇÃO", "SETOR",
               "SUBSETOR"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self, ticket, type_asset):
        """
        Summary.

        Function to retrieve the stocks and reits prices infos.
        ticket: String. Ticket code.
        type_asset: String. "STOCK" or "REIT".
        """
        soup, dom = self._get_soup(ticket, type_asset)
        df1 = self._parse_common_data(soup, dom, ticket)
        df2 = self._parse_cards(soup)[1]  # Price.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO USD", "COTAÇÃO BRL"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VARIAÇÃO DE COTAÇÃO USD 1 ANO"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self, ticket, type_asset):
        """
        Summary.

        Function to retrieve the stocks and reits kpi's infos.
        ticket: String. Ticket code.
        type_asset: String. "STOCK" or "REIT".
        """
        soup, dom = self._get_soup(ticket, type_asset)
        df1 = self._parse_common_data(soup, dom, ticket)
        df1 = df1.drop([2])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([0, 1, 2, 3, 4, 5, 11, 12])  # Necessary rows.
        df3 = self._parse_cards(soup)[2]  # KPI.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)

        tmp = ["VALOR DE MERCADO USD", "PATRIMÔNIO LÍQUIDO USD", "P/EBITDA",
               "ATIVOS USD", "QUANTIDADE DE PAPÉIS", "LIQUIDEZ USD", "P/L",
               "P/RECEITA LÍQUIDA", "P/VP", "P/EBIT", "P/ATIVO", "VPA", "LPA",
               "PATRIMÔNIO LÍQUIDO/ATIVOS"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["DIVIDEND YIELD", "ROA", "ROE", "ROIC", "MARGEM LÍQUIDA",
               "MARGEM BRUTA", "MARGEM OPERACIONAL", "CAGR RECEITAS 5 ANOS",
               "CAGR LUCROS 5 ANOS"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self, ticket, type_asset):
        """
        Summary.

        Function to aggregate the stocks and reits full infos.
        ticket: String. Ticket code.
        """
        df = pd.concat([self.info(ticket, type_asset),
                        self.price(ticket, type_asset),
                        self.kpi(ticket, type_asset)])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        df = df.drop(["INFO"], axis=1)
        return df


class ETFs:
    """
    Summary.

    Retrieve the ETF's companies infos.
    """

    def __init__(self):
        self.url = "https://investidor10.com.br/etfs-global/{}"
        self.aux = pd.read_parquet("INVESTIDOR10_ETFS.parquet")

    def _get_soup(self, ticket):
        url = self.url.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200:
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, soup, dom, ticket):
        nome = dom.xpath("/html/body/div[4]/main/header/div[2]/div/" +
                         "div[1]/div[2]/h2")
        nome = (nome[0].text.upper().strip()
                if nome and nome[0].text else None)
        cotacao_brl = dom.xpath("/html/body/div[4]/main/section/div/" +
                                "section[1]/div[1]/div[2]/div/span[2]")
        cotacao_brl = (cotacao_brl[0].text.upper().strip()
                       if cotacao_brl and cotacao_brl[0].text else None)
        infos = []
        infos.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        infos.append({"INFO": "NOME", "VALOR": nome})
        infos.append({"INFO": "MOEDA", "VALOR": "USD"})
        infos.append({"INFO": "COTAÇÃO BRL", "VALOR": cotacao_brl})
        df = pd.DataFrame(infos)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
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
        price = aux.clean_cards(price)
        return price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        column_mapping = {
            "COTAÇÃO": "COTAÇÃO USD", "DY": "DIVIDEND YIELD",
            "CAPITALIZAÇÃO": "VALOR DE MERCADO USD",
            "VARIAÇÃO (12M)": "VARIAÇÃO DE COTAÇÃO USD 1 ANO",
            "VARIAÇÃO (60N)": "VARIAÇÃO DE COTAÇÃO USD 5 ANOS"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian ETF's infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df = self._parse_common_data(soup, dom, ticket)
        df = df.drop([2, 3])  # Necessary rows.
        return df

    def price(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian ETF's prices infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df1 = self.aux
        df1 = df1[df1["ATIVO"] == ticket.strip().upper()]
        df1 = df1[["VARIAÇÃO DE COTAÇÃO USD 1 MÊS"]]
        df1 = df1.reset_index(drop=True)
        df1 = df1.T.reset_index(drop=False)
        df1 = df1.rename(columns={"index": "INFO", 0: "VALOR"})
        df2 = self._parse_common_data(soup, dom, ticket)
        df2 = df2.drop([1])  # Necessary rows.
        df3 = self._parse_cards(soup)  # Price.
        df3 = df3.drop([1, 4])  # Necessary rows.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO BRL", "COTAÇÃO USD"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VARIAÇÃO DE COTAÇÃO USD 1 ANO",
               "VARIAÇÃO DE COTAÇÃO USD 5 ANOS"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian ETF's kpi's infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df1 = self.aux
        df1 = df1[df1["ATIVO"] == ticket.strip().upper()]
        df1 = df1[["VOLUME USD", "LIQUIDEZ USD"]]
        df1 = df1.reset_index(drop=True)
        df1 = df1.T.reset_index(drop=False)
        df1 = df1.rename(columns={"index": "INFO", 0: "VALOR"})
        df2 = self._parse_common_data(soup, dom, ticket)
        df2 = df2.drop([1, 3])  # Necessary rows.
        df3 = self._parse_cards(soup)  # Price.
        df3 = df3.drop([0, 2, 3])  # Necessary rows.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)

        tmp = ["DIVIDEND YIELD"]
        df = aux.string_columns(df, tmp)
        df["VALOR DE MERCADO USD"] = (df["VALOR DE MERCADO USD"]
                                      .str.replace("US$\n", "", regex=False))
        df["VALOR DE MERCADO USD"] = df["VALOR DE MERCADO USD"].apply(aux
                                                                      .times2)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self, ticket):
        """
        Summary.

        Function to aggregate the brazilian ETF's full infos.
        ticket: String. Ticket code.
        """
        df = pd.concat([self.info(ticket), self.price(ticket),
                        self.kpi(ticket)])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        df = df.drop(["INFO"], axis=1)
        return df


'''
a = assets_auxtable(type_asset="ACAO")
b = assets_auxtable(type_asset="FII")
c = assets_auxtable(type_asset="STOCK")
d = assets_auxtable(type_asset="REIT")
e = etfbr_auxtable()
f = etf_auxtable()
'''

z = StocksBR()
t = "wege3"
a = z.info(ticket=t)
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.table(ticket=t)
'''
z = ReitsBR()
t = "visc11"
a = z.info(ticket=t)
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.table(ticket=t)

z = ETFsBR()
t = "ivvb11"
a = z.info(ticket=t)
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.table(ticket=t)

z = StocksReits()
t = "msft"
a = z.info(ticket=t, type_asset="STOCK")
b = z.price(ticket=t, type_asset="STOCK")
c = z.kpi(ticket=t, type_asset="STOCK")
d = z.table(ticket=t, type_asset="STOCK")

z = StocksReits()
t = "o"
a = z.info(ticket=t, type_asset="REIT")
b = z.price(ticket=t, type_asset="REIT")
c = z.kpi(ticket=t, type_asset="REIT")
d = z.table(ticket=t, type_asset="REIT")

z = ETFs()
t = "vt"
a = z.info(ticket=t)
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.table(ticket=t)
'''
