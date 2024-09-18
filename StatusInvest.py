"""
Summary.

Retrieve the companies infos from Status Invest website.
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


class StocksBR:
    """
    Summary.

    Retrieve the brazilian stocks companies infos.
    """

    def __init__(self):
        self.url = "https://statusinvest.com.br/acoes/{}"

    def _get_soup(self, ticket):
        url = self.url.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom, ticket):
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
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        tmp.append({"INFO": "EMPRESA", "VALOR": empresa})
        tmp.append({"INFO": "CNPJ", "VALOR": cnpj})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        tmp.append({"INFO": "TIPO ATIVO", "VALOR": tipo_ativo})
        tmp.append({"INFO": "TAG ALONG", "VALOR": tag_along})
        df = pd.DataFrame(tmp)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
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
        company = aux.clean_cards(company)

        # Price.
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
        price = price.drop([3])  # Removing unnecessary row if any.
        price = aux.clean_cards(price)

        # KPI.
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
        kpi = aux.clean_cards(kpi)
        return company, price, kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
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
            "LIQ. CORRENTE": "LIQUIDEZ CORRENTE",
            "SEGMENTO DE ATUAÇÃO": "SEGMENTO"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian stocks infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket=ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([3, 5])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])  # Necessary rows.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["TIPO ATIVO", "EMPRESA", "CNPJ", "SETOR", "SUBSETOR",
               "SEGMENTO", "SEGMENTO DE LISTAGEM"]
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
        soup, dom = self._get_soup(ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1, 2, 4, 5])  # Necessary rows.
        df1 = aux.clean_cards(df1)
        df2 = self._parse_cards(soup)[1]  # Price.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS",
               "DIVIDENDOS PAGOS 1 ANO"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VALORIZAÇÃO DE COTAÇÃO 1 ANO", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS"]
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
        soup, dom = self._get_soup(ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1, 2, 4])  # Necessary rows.
        df1 = aux.clean_cards(df1)
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([11, 12, 13])  # Necessary rows.
        df3 = self._parse_cards(soup)[2]  # KPI.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)

        tmp = ["PATRIMÔNIO LÍQUIDO", "ATIVOS", "ATIVO CIRCULANTE",
               "DÍVIDA BRUTA", "DISPONIBILIDADE", "DÍVIDA LÍQUIDA",
               "VALOR DE MERCADO", "VALOR DE FIRMA", "QUANTIDADE DE PAPÉIS",
               "P/L", "PEG RATIO", "P/VP", "EV/EBITDA", "EV/EBIT", "P/EBITDA",
               "P/EBIT", "VPA", "P/ATIVO", "LPA", "P/RECEITA LÍQUIDA",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "DÍVIDA LÍQUIDA/EBITDA",
               "DÍVIDA LÍQUIDA/EBIT", "PATRIMÔNIO LÍQUIDO/ATIVOS",
               "PASSIVOS/ATIVOS", "LIQUIDEZ CORRENTE", "GIRO ATIVOS"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["EMPRESA", "DIVIDEND YIELD", "MARGEM BRUTA", "ROIC", "ROA",
               "MARGEM EBITDA", "MARGEM EBIT", "MARGEM LÍQUIDA", "ROE",
               "CAGR RECEITAS 5 ANOS", "CAGR LUCROS 5 ANOS", "FREE FLOAT",
               "TAG ALONG"]
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
        self.url = "https://statusinvest.com.br/fundos-imobiliarios/{}"

    def _get_soup(self, ticket):
        url = self.url.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom, ticket):
        administrador = dom.xpath("/html/body/main/div[3]/div/div/" +
                                  "div[3]/div/div[2]/div[1]/div/strong")
        administrador = (administrador[0].text.upper().strip()
                         if administrador and administrador[0].text
                         else None)
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        tmp.append({"INFO": "ADMINISTRADOR", "VALOR": administrador})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        df = pd.DataFrame(tmp)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
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
        company = aux.clean_cards(company)

        # Price.
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
        price = aux.clean_cards(price)

        # KPI.
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
        kpi = aux.clean_cards(kpi)
        return company, price, kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        column_mapping = {
            "VALOR ATUAL": "COTAÇÃO",
            "MIN. 52 SEMANAS": "COTAÇÃO MÍNIMA 1 ANO",
            "MÁX. 52 SEMANAS": "COTAÇÃO MÁXIMA 1 ANO",
            "VALORIZAÇÃO (12M)": "VALORIZAÇÃO DE COTAÇÃO 1 ANO",
            "MIN. MÊS": "COTAÇÃO MÍNIMA 1 MÊS",
            "MÁX. MÊS": "COTAÇÃO MÁXIMA 1 MÊS",
            "VALOR EM CAIXA": "VALOR EM CAIXA %",
            "Nº DE COTAS": "QUANTIDADE DE COTAS",
            "TIPO DA GESTÃO": "GESTÃO", "TIPO ANBIMA": "MANDATO",
            "ÚLTIMOS 12 MESES": "DIVIDENDOS PAGOS 1 ANO",
            "MÊS ATUAL": "VALORIZAÇÃO DE COTAÇÃO 1 MÊS",
            "VAL. PATRIMONIAL P/COTA": "VALOR PATRIMONIAL/COTA",
            "NOME PREGÃO": "NOME", "VALOR MERCADO": "VALOR DE MERCADO",
            "Nº DE COTISTAS": "QUANTIDADE DE COTISTAS",
            "DY CAGR(5 ANOS)": "CAGR DIVIDEND YIELD 5 ANOS",
            "VALOR CAGR(5 ANOS)": "CAGR 5 ANOS",
            "ÍNICIO DO FUNDO": "DATA DE CRIAÇÃO", "SEGMENTO": "SEGMENTO 2",
            "TOTAL": "VALOR EM CAIXA", "SEGMENTO ANBIMA": "SEGMENTO",
            "LIQUIDEZ MÉDIA DIÁRIA": "LIQUIDEZ",
            "RENDIM. MÉDIO (24M)": "RENDIMENTO MÉDIO 2 ANOS",
            "TAXAS ADMINISTRAÇÃO": "TAXA ADMINISTRATIVA",
            "PATRIMÔNIO": "VALOR PATRIMONIAL"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian reits infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([2])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([9, 11])  # Necessary rows.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        df["MANDATO"] = df["MANDATO"].str.replace("HÍBRIDOS", "HÍBRIDO")
        df["DATA DE CRIAÇÃO"] = pd.to_datetime(df["DATA DE CRIAÇÃO"],
                                               format="%d/%m/%Y",
                                               errors="coerce").dt.date

        tmp = ["ADMINISTRADOR", "CNPJ", "NOME", "SEGMENTO 2", "GESTÃO",
               "TAXA ADMINISTRATIVA", "PRAZO DE DURAÇÃO", "MANDATO",
               "SEGMENTO", "PÚBLICO-ALVO"]
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
        soup, dom = self._get_soup(ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1])  # Necessary rows.
        df1 = aux.clean_cards(df1)
        df2 = self._parse_cards(soup)[1]  # Price.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS",
               "DIVIDENDOS PAGOS 1 ANO", "DIVIDEND YIELD"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VALORIZAÇÃO DE COTAÇÃO 1 ANO", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS"]
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
        soup, dom = self._get_soup(ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1])  # Necessary rows.
        df1 = aux.clean_cards(df1)
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([0, 1, 2, 3, 4, 5, 6, 7, 8, 10])  # Necessary rows.
        df3 = self._parse_cards(soup)[2]  # KPI.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)
        df["VALOR EM CAIXA %"] = df["VALOR EM CAIXA %"].apply(
            lambda x: f"{x}%" if pd.notna(x) else x)

        tmp = ["RENDIMENTO MÉDIO 2 ANOS", "LIQUIDEZ", "VALOR PATRIMONIAL/COTA",
               "P/VP", "VALOR EM CAIXA", "CAGR DIVIDEND YIELD 3 ANOS",
               "CAGR 3 ANOS", "QUANTIDADE DE COTISTAS", "VALOR PATRIMONIAL",
               "CAGR 5 ANOS", "VALOR DE MERCADO", "QUANTIDADE DE COTAS",
               "CAGR DIVIDEND YIELD 5 ANOS"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VALOR EM CAIXA %"]
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
        self.url = "https://statusinvest.com.br/etfs/{}"

    def _get_soup(self, ticket):
        url = self.url.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom, ticket):
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
        tmp.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        tmp.append({"INFO": "NOME", "VALOR": nome})
        tmp.append({"INFO": "MOEDA", "VALOR": "BRL"})
        tmp.append({"INFO": "ADMINISTRADOR", "VALOR": administrador})
        tmp.append({"INFO": "GESTOR", "VALOR": gestor})
        tmp.append({"INFO": "ÍNDICE", "VALOR": indice})
        df = pd.DataFrame(tmp)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
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
        company = aux.clean_cards(company)

        # Price.
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
        price = aux.clean_cards(price)
        return company, price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
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

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian ETF's infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([2])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([0, 2, 3, 4, 5, 6, 7, 8])  # Necessary rows.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)
        df["DATA DE CRIAÇÃO"] = pd.to_datetime(df["DATA DE CRIAÇÃO"],
                                               format="%d/%m/%Y",
                                               errors="coerce").dt.date

        tmp = ["TAXA ADMINISTRATIVA"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian ETF's prices infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1, 3, 4, 5])  # Necessary rows.
        df2 = self._parse_cards(soup)[1]  # Price.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO", "COTAÇÃO MÍNIMA 1 ANO", "COTAÇÃO MÁXIMA 1 ANO",
               "COTAÇÃO MÍNIMA 1 MÊS", "COTAÇÃO MÁXIMA 1 MÊS",
               "DIVIDENDOS PAGOS 1 ANO"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VALORIZAÇÃO DE COTAÇÃO 1 ANO", "VALORIZAÇÃO DE COTAÇÃO 1 MÊS"]
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
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1, 3, 4, 5])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([0, 1, 9, 10, 11, 12, 13])  # Necessary rows.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["PATRIMÔNIO LÍQUIDO", "TOTAL EM CARTEIRA", "LIQUIDEZ", "RATIO",
               "LOTE PADRÃO", "LOTE MÍNIMO", "QUANTIDADE DE COTISTAS"]
        df = aux.numeric_columns(df, tmp)
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
        self.urls = "https://statusinvest.com.br/acoes/eua/{}"
        self.urlr = "https://statusinvest.com.br/reits/{}"

    def _get_soup(self, ticket, type_asset):
        if type_asset == "STOCK":
            url = self.urls.format(ticket.lower())
        else:
            url = self.urlr.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom, ticket):
        tipo_ativo = dom.xpath("/html/body/main/header/div[2]/div/" +
                               "div[1]/div[1]/span")
        tipo_ativo = (tipo_ativo[0].text.upper().strip()
                      if tipo_ativo and tipo_ativo[0].text else None)
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        tmp.append({"INFO": "TIPO ATIVO", "VALOR": tipo_ativo})
        tmp.append({"INFO": "MOEDA", "VALOR": "USD"})
        df = pd.DataFrame(tmp)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
        # Company 1.
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
        company = aux.clean_cards(company)

        # Price.
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
        price = price.drop([3])  # Removing unnecessary row if any.
        price = aux.clean_cards(price)

        # KPIs
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
        kpi = aux.clean_cards(kpi)
        return company, price, kpi

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
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
            "LIQ. CORRENTE": "LIQUIDEZ CORRENTE",
            "P/ATIVO CIRC. LIQ.": "P/ATIVO CIRCULANTE LÍQUIDO",
            "DÍV. LÍQUIDA/PL": "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO",
            "DÍV. LÍQUIDA/EBITDA": "DÍVIDA LÍQUIDA/EBITDA",
            "DÍV. LÍQUIDA/EBIT": "DÍVIDA LÍQUIDA/EBIT",
            "PL/ATIVOS": "PATRIMÔNIO LÍQUIDO/ATIVOS"}
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
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([2])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([7, 8, 9, 10, 11, 12, 13, 14])  # Necessary rows.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["TIPO ATIVO", "EMPRESA", "MERCADO", "SETOR EUA", "SEGMENTO",
               "SUBSETOR EUA", "SETOR", "SUBSETOR"]
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
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1])  # Necessary rows.
        df2 = self._parse_cards(soup)[1]  # Price.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO USD", "COTAÇÃO MÍNIMA USD 1 ANO",
               "COTAÇÃO MÁXIMA USD 1 ANO", "COTAÇÃO MÍNIMA USD 1 MÊS",
               "COTAÇÃO MÁXIMA USD 1 MÊS", "DIVIDENDOS PAGOS USD 1 ANO"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS"]
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
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1])  # Necessary rows.
        df2 = self._parse_cards(soup)[0]  # Company.
        df2 = df2.drop([0, 1, 2, 3, 4, 5, 6])  # Necessary rows.
        df3 = self._parse_cards(soup)[2]  # KPI.
        df = pd.concat([df1, df2, df3])
        df = self._adjust_columns(df)

        tmp = ["PATRIMÔNIO LÍQUIDO USD", "ATIVOS USD", "ATIVO CIRCULANTE USD",
               "DÍVIDA BRUTA USD", "DISPONIBILIDADE USD", "DÍVIDA LÍQUIDA USD",
               "VALOR DE MERCADO USD", "VALOR DE FIRMA USD", "GIRO ATIVOS",
               "P/L", "PEG RATIO", "P/VP", "EV/EBITDA", "EV/EBIT", "P/EBITDA",
               "P/EBIT", "VPA", "P/ATIVO", "LPA", "P/RECEITA LÍQUIDA",
               "P/CAPITAL DE GIRO", "P/ATIVO CIRCULANTE LÍQUIDO",
               "DÍVIDA LÍQUIDA/PATRIMÔNIO LÍQUIDO", "DÍVIDA LÍQUIDA/EBITDA",
               "DÍVIDA LÍQUIDA/EBIT", "PATRIMÔNIO LÍQUIDO/ATIVOS",
               "PASSIVOS/ATIVOS", "LIQUIDEZ CORRENTE"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["DIVIDEND YIELD", "ROE", "ROA", "ROIC", "MARGEM BRUTA",
               "MARGEM EBITDA", "MARGEM EBIT", "MARGEM LÍQUIDA",
               "CAGR RECEITAS 5 ANOS", "CAGR LUCROS 5 ANOS"]
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
        self.url = "https://statusinvest.com.br/etf/eua/{}"

    def _get_soup(self, ticket):
        url = self.url.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        dom = etree.HTML(str(soup))
        # Checking if asset exist.
        if page.status_code != 200 or soup.find_all(string="OPS. . ."):
            raise ValueError("Asset does not exist")
        return soup, dom

    def _parse_common_data(self, dom, ticket):
        nome = dom.xpath("/html/body/main/header/div[2]/div/div[1]/h1/" +
                         "small")
        nome = (nome[0].text.upper().strip()
                if nome and nome[0].text else None).split("-")[0]
        tmp = []
        tmp.append({"INFO": "TICKET", "VALOR": ticket.strip().upper()})
        tmp.append({"INFO": "NOME", "VALOR": nome})
        tmp.append({"INFO": "MOEDA", "VALOR": "USD"})
        df = pd.DataFrame(tmp)
        df = aux.clean_cards(df)
        return df

    def _parse_cards(self, soup):
        # Price.
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
        price = aux.clean_cards(price)
        return price

    def _adjust_columns(self, df):
        df = df.T  # Transposing.
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        column_mapping = {
            "VALOR ATUAL": "COTAÇÃO USD",
            "MÊS ATUAL": "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS",
            "MÁX. MÊS": "COTAÇÃO MÁXIMA USD 1 MÊS",
            "MIN. 52 SEMANAS": "COTAÇÃO MÍNIMA USD 1 ANO",
            "MÁX. 52 SEMANAS": "COTAÇÃO MÁXIMA USD 1 ANO",
            "VALORIZAÇÃO (12M)": "VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
            "ÚLTIMOS 12 MESES": "DIVIDENDOS PAGOS USD 1 ANO",
            "MÁX. MÊS": "COTAÇÃO MÁXIMA USD 1 MÊS",
            "MIN. MÊS": "COTAÇÃO MÍNIMA USD 1 MÊS"}
        df = df.rename(columns=column_mapping)
        return df

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the ETF's infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df = self._parse_common_data(dom, ticket)
        df = df.drop([2])  # Necessary rows.
        df = self._adjust_columns(df)

        tmp = ["NOME"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self, ticket):
        """
        Summary.

        Function to retrieve the ETF's prices infos.
        ticket: String. Ticket code.
        """
        soup, dom = self._get_soup(ticket)
        df1 = self._parse_common_data(dom, ticket)
        df1 = df1.drop([1])  # Necessary rows.
        df2 = self._parse_cards(soup)  # Price.
        df = pd.concat([df1, df2])
        df = self._adjust_columns(df)

        tmp = ["COTAÇÃO USD", "COTAÇÃO MÍNIMA USD 1 ANO",
               "COTAÇÃO MÁXIMA USD 1 ANO", "COTAÇÃO MÍNIMA USD 1 MÊS",
               "COTAÇÃO MÁXIMA USD 1 MÊS", "DIVIDENDOS PAGOS USD 1 ANO"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["VALORIZAÇÃO DE COTAÇÃO USD 1 ANO",
               "VALORIZAÇÃO DE COTAÇÃO USD 1 MÊS"]
        df = aux.string_columns(df, tmp)
        df = df.T.reset_index(drop=False)
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def table(self, ticket):
        """
        Summary.

        Function to aggregate the ETF's full infos.
        ticket: String. Ticket code.
        """
        df = pd.concat([self.info(ticket), self.price(ticket)])
        df = df.drop_duplicates()  # Remove duplicates.
        df = df.T.reset_index(drop=False)
        df.columns = df.iloc[0]  # First row as column name.
        df = df.iloc[1:]  # Removing frist row.
        df = df.drop(["INFO"], axis=1)
        return df


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
c = z.table(ticket=t)
'''
