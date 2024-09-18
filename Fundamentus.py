"""
Summary.

Retrieve the companies infos from Fundamentus website.
"""
# -*- coding: utf-8 -*-

import Auxiliaries as aux
from bs4 import BeautifulSoup
from datetime import timedelta
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
        self.urlr = "https://www.fundamentus.com.br/resultado.php"
        self.urlp = ("https://www.fundamentus.com.br/proventos.php?" +
                     "papel={}+&tipo=2")

    def _get_soup(self, ticket, type_table):
        if type_table == "KPI":
            url = self.urlr
        else:
            url = self.urlp.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        # Checking if asset exist.
        if (page.status_code != 200
            or soup.find_all(string=lambda text: text and
                             "Nenhum provento encontrado" in text)):
            raise ValueError("Info does not exist")
        return soup

    def _parse_table_info(self, soup):
        # Table.
        webtable = soup.find("table")  # Getting <table>.
        tmp = []
        for webtable_row in webtable.tbody.find_all("tr"):  # Getting <tr>.
            webtable_column = webtable_row.find_all("td")  # Getting <td>.
            if webtable_column:
                ticket = webtable_column[0].text.strip(" ")
                cotacao = webtable_column[1].text.strip(" ")
                p_l = webtable_column[2].text.strip(" ")
                p_vp = webtable_column[3].text.strip(" ")
                psr = webtable_column[4].text.strip(" ")
                dy = webtable_column[5].text.strip(" ")
                p_ativo = webtable_column[6].text.strip(" ")
                p_capgiro = webtable_column[7].text.strip(" ")
                p_ebit = webtable_column[8].text.strip(" ")
                p_atvcircliq = webtable_column[9].text.strip(" ")
                ev_ebit = webtable_column[10].text.strip(" ")
                ev_ebitda = webtable_column[11].text.strip(" ")
                margem_ebit = webtable_column[12].text.strip(" ")
                margem_liq = webtable_column[13].text.strip(" ")
                liq_cor = webtable_column[14].text.strip(" ")
                roic = webtable_column[15].text.strip(" ")
                roe = webtable_column[16].text.strip(" ")
                liquidez = webtable_column[17].text.strip(" ")
                patr_liq = webtable_column[18].text.strip(" ")
                divbruta_patr = webtable_column[19].text.strip(" ")
                cagr_receita_5a = webtable_column[20].text.strip(" ")
                tmp.append({
                    "TICKET": str.strip(ticket), "COTAÇÃO": str.strip(cotacao),
                    "P/L": str.strip(p_l), "P/VP": str.strip(p_vp),
                    "PSR": str.strip(psr), "DIVIDEND YIELD": str.strip(dy),
                    "P/ATIVO": str.strip(p_ativo), "ROIC": str.strip(roic),
                    "P/CAPITAL DE GIRO": str.strip(p_capgiro),
                    "P/EBIT": str.strip(p_ebit), "ROE": str.strip(roe),
                    "P/ATIVO CIRCULANTE LÍQUIDO": str.strip(p_atvcircliq),
                    "EV/EBIT": str.strip(ev_ebit),
                    "LIQUIDEZ": str.strip(liquidez),
                    "EV/EBITDA": str.strip(ev_ebitda),
                    "MARGEM EBIT": str.strip(margem_ebit),
                    "MARGEM LÍQUIDA": str.strip(margem_liq),
                    "LIQUIDEZ CORRENTE": str.strip(liq_cor),
                    "PATRIMÔNIO LÍQUIDO": str.strip(patr_liq),
                    "DÍVIDA BRUTA/PATRIMÔNIO": str.strip(divbruta_patr),
                    "CAGR RECEITA 5 ANOS": str.strip(cagr_receita_5a)
                    })
        table = pd.DataFrame(tmp)  # Temporary dataframe.
        return table

    def _parse_table_payment(self, soup):
        # Table.
        webtable = soup.find("table")  # Getting <table>.
        tmp = []
        for webtable_row in webtable.tbody.find_all("tr"):  # Getting <tr>.
            webtable_column = webtable_row.find_all("td")  # Getting <td>.
            if webtable_column:
                data_com = webtable_column[0].text.strip(" ")
                valor = webtable_column[1].text.strip(" ")
                tipo_provento = webtable_column[2].text.strip(" ")
                data_pagamento = webtable_column[3].text.strip(" ")
                qtd_acoes = webtable_column[4].text.strip(" ")
                tmp.append({
                    "DATA COM": str.strip(data_com), "QTD AÇÕES": qtd_acoes,
                    "VALOR": str.strip(valor),
                    "TIPO PROVENTO": str.upper(tipo_provento),
                    "DATA PAGAMENTO": str.strip(data_pagamento),
                    })
        table = pd.DataFrame(tmp)  # Temporary dataframe.
        return table

    def table(self, ticket=None):
        """
        Summary.

        Function to aggregate the brazilian stocks full infos.
        """
        soup = self._get_soup(ticket, type_table="KPI")
        df = self._parse_table_info(soup)  # Table info.

        tmp = ["COTAÇÃO", "P/L", "P/VP", "PSR", "P/ATIVO", "P/CAPITAL DE GIRO",
               "P/EBIT", "P/ATIVO CIRCULANTE LÍQUIDO", "EV/EBIT", "LIQUIDEZ",
               "EV/EBITDA", "LIQUIDEZ CORRENTE", "PATRIMÔNIO LÍQUIDO",
               "DÍVIDA BRUTA/PATRIMÔNIO"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["TICKET", "DIVIDEND YIELD", "ROIC", "ROE", "MARGEM EBIT",
               "MARGEM LÍQUIDA", "CAGR RECEITA 5 ANOS"]
        df = aux.string_columns(df, tmp)
        return df

    def price(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian stocks prices infos.
        ticket: String. Ticket code.
        """
        df = self.table(ticket)
        df = df[["TICKET", "COTAÇÃO"]]
        df = (df[df["TICKET"] == str.upper(ticket)].reset_index(drop=True))
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian stocks kpi's infos.
        ticket: String. Ticket code.
        """
        df = self.table(ticket)
        df = df[["TICKET", "P/L", "P/VP", "PSR", "P/ATIVO",
                 "P/CAPITAL DE GIRO", "P/EBIT", "P/ATIVO CIRCULANTE LÍQUIDO",
                 "EV/EBIT", "LIQUIDEZ", "EV/EBITDA", "LIQUIDEZ CORRENTE",
                 "PATRIMÔNIO LÍQUIDO", "DÍVIDA BRUTA/PATRIMÔNIO",
                 "DIVIDEND YIELD", "ROIC", "ROE", "MARGEM EBIT",
                 "MARGEM LÍQUIDA", "CAGR RECEITA 5 ANOS"]]
        df = (df[df["TICKET"] == str.upper(ticket)].reset_index(drop=True))
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def payments(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian stocks payments infos.
        ticket: String. Ticket code.
        """
        soup = self._get_soup(ticket, "PAYMENT")
        df = self._parse_table_payment(soup)  # Table info.
        df = df[df["DATA COM"] != "-"]
        tmp = ["QTD AÇÕES", "VALOR"]
        for column in tmp:
            df[column] = df[column].str.replace(".", "")
            df[column] = df[column].str.replace(",", ".")
            df[column] = pd.to_numeric(df[column], errors="coerce")
            # df = df.astype({column: float})
            # df[column] = round(df[column], 2)

        tmp = ["DATA COM", "DATA PAGAMENTO"]
        for column in tmp:
            df[column] = pd.to_datetime(df[column], format="%d/%m/%Y",
                                        errors="coerce").dt.date

        df["DATA EX"] = df["DATA COM"]+timedelta(days=1)
        tmp = ["DATA COM", "DATA EX", "DATA PAGAMENTO"]
        for column in tmp:
            df[column] = df[column].astype(str)
            df[column] = df[column].replace("NaT", None)

        df["VALOR"] = df["VALOR"]/df["QTD AÇÕES"]
        df = df[df["VALOR"] > 0]  # Necessary rows.
        df["ATIVO"] = ticket.upper()
        df = df.sort_values(by=["ATIVO", "DATA COM"],
                            ascending=[True, False])  # Sort rows.
        df = df[["ATIVO", "DATA COM", "DATA EX", "DATA PAGAMENTO", "VALOR",
                 "TIPO PROVENTO"]]  # Reorder dataframe.
        return df


class ReitsBR:
    """
    Summary.

    Retrieve the brazilian reits companies infos.
    """

    def __init__(self):
        self.urlr = "https://www.fundamentus.com.br/fii_resultado.php"
        self.urlp = ("https://www.fundamentus.com.br/fii_proventos.php?" +
                     "papel={}&tipo=2")

    def _get_soup(self, ticket, type_table):
        if type_table == "KPI":
            url = self.urlr
        else:
            url = self.urlp.format(ticket.lower())
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        # Checking if asset exist.
        if (page.status_code != 200
            or soup.find_all(string=lambda text: text and
                             "Nenhum provento encontrado" in text)):
            raise ValueError("Info does not exist")
        return soup

    def _parse_table_info(self, soup):
        # Table.
        webtable = soup.find("table")  # Getting <table>.
        tmp = []
        for webtable_row in webtable.tbody.find_all("tr"):  # Getting <tr>.
            webtable_column = webtable_row.find_all("td")  # Getting <td>.
            if webtable_column:
                ticket = webtable_column[0].text.strip(" ")
                segmento = webtable_column[1].text.strip(" ").upper()
                cotacao = webtable_column[2].text.strip(" ")
                ffoy = webtable_column[3].text.strip(" ")
                dy = webtable_column[4].text.strip(" ")
                p_vp = webtable_column[5].text.strip(" ")
                valormercado = webtable_column[6].text.strip(" ")
                liquidez = webtable_column[7].text.strip(" ")
                qtdimoveis = webtable_column[8].text.strip(" ")
                precom2 = webtable_column[9].text.strip(" ")
                aluguelm2 = webtable_column[10].text.strip(" ")
                caprate = webtable_column[11].text.strip(" ")
                vacancia = webtable_column[12].text.strip(" ")
                tmp.append({
                    "TICKET": str.strip(ticket), "COTAÇÃO": str.strip(cotacao),
                    "SEGMENTO": str.strip(segmento), "P/VP": str.strip(p_vp),
                    "LUCRO LÍQUIDO AJUSTADO/VALOR DE MERCADO": str.strip(ffoy),
                    "DIVIDEND YIELD": str.strip(dy),
                    "VALOR DE MERCADO": str.strip(valormercado),
                    "LIQUIDEZ": str.strip(liquidez),
                    "QUANTIDADE DE IMÓVEIS": str.strip(qtdimoveis),
                    "PREÇO M2": str.strip(precom2),
                    "ALUGUEL M2": str.strip(aluguelm2),
                    "CAP RATE": str.strip(caprate),
                    "VACÂNCIA": str.strip(vacancia),
                    })
        table = pd.DataFrame(tmp)  # Temporary dataframe.
        return table

    def _parse_table_payment(self, soup):
        # Table.
        webtable = soup.find("table")  # Getting <table>.
        tmp = []
        for webtable_row in webtable.tbody.find_all("tr"):  # Getting <tr>.
            webtable_column = webtable_row.find_all("td")  # Getting <td>.
            if webtable_column:
                data_com = webtable_column[0].text.strip(" ")
                valor = webtable_column[3].text.strip(" ")
                tipo_provento = webtable_column[1].text.strip(" ")
                data_pagamento = webtable_column[2].text.strip(" ")
                tmp.append({"VALOR": str.strip(valor),
                            "DATA COM": str.strip(data_com),
                            "TIPO PROVENTO": str.upper(tipo_provento),
                            "DATA PAGAMENTO": str.strip(data_pagamento)
                            })
        table = pd.DataFrame(tmp)  # Temporary dataframe.
        return table

    def table(self, ticket=None):
        """
        Summary.

        Function to aggregate the brazilian reits full infos.
        """
        soup = self._get_soup(ticket, type_table="KPI")
        df = self._parse_table_info(soup)  # Table info.

        tmp = ["COTAÇÃO", "P/VP", "VALOR DE MERCADO", "LIQUIDEZ", "ALUGUEL M2",
               "QUANTIDADE DE IMÓVEIS", "PREÇO M2"]
        df = aux.numeric_columns(df, tmp)

        tmp = ["TICKET", "SEGMENTO", "LUCRO LÍQUIDO AJUSTADO/VALOR DE MERCADO",
               "DIVIDEND YIELD", "CAP RATE", "VACÂNCIA"]
        df = aux.string_columns(df, tmp)
        return df

    def info(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian reits infos.
        ticket: String. Ticket code.
        """
        df = self.table(ticket)
        df = df[["TICKET", "SEGMENTO"]]
        df = (df[df["TICKET"] == str.upper(ticket)].reset_index(drop=True))
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def price(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian reits prices infos.
        ticket: String. Ticket code.
        """
        df = self.table(ticket)
        df = df[["TICKET", "COTAÇÃO"]]
        df = (df[df["TICKET"] == str.upper(ticket)].reset_index(drop=True))
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def kpi(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian reits kpi's infos.
        ticket: String. Ticket code.
        """
        df = self.table(ticket)
        df = df[["TICKET", "P/VP", "VALOR DE MERCADO", "LIQUIDEZ",
                 "ALUGUEL M2", "QUANTIDADE DE IMÓVEIS", "PREÇO M2",
                 "LUCRO LÍQUIDO AJUSTADO/VALOR DE MERCADO", "DIVIDEND YIELD",
                 "CAP RATE", "VACÂNCIA"]]
        df = (df[df["TICKET"] == str.upper(ticket)].reset_index(drop=True))
        df = df.T.reset_index(drop=False)
        df = df.rename(columns={"index": "INFO", 0: "VALOR"})
        df["VALOR"] = df["VALOR"].fillna("SEM INFORMAÇÃO")
        return df

    def payments(self, ticket):
        """
        Summary.

        Function to retrieve the brazilian reits payments infos.
        ticket: String. Ticket code.
        """
        soup = self._get_soup(ticket, "PAYMENT")
        df = self._parse_table_payment(soup)  # Table info.
        df = df[df["DATA COM"] != "-"]
        tmp = ["VALOR"]
        for column in tmp:
            df[column] = df[column].str.replace(".", "")
            df[column] = df[column].str.replace(",", ".")
            df[column] = pd.to_numeric(df[column], errors="coerce")
            # df = df.astype({column: float})
            # df[column] = round(df[column], 2)

        tmp = ["DATA COM", "DATA PAGAMENTO"]
        for column in tmp:
            df[column] = pd.to_datetime(df[column], format="%d/%m/%Y",
                                        errors="coerce").dt.date

        df["DATA EX"] = df["DATA COM"]+timedelta(days=1)
        tmp = ["DATA COM", "DATA EX", "DATA PAGAMENTO"]
        for column in tmp:
            df[column] = df[column].astype(str)
            df[column] = df[column].replace("NaT", None)

        df["VALOR"] = df["VALOR"]
        df = df[df["VALOR"] > 0]  # Necessary rows.
        df["ATIVO"] = ticket.upper()
        df = df.sort_values(by=["ATIVO", "DATA COM"],
                            ascending=[True, False])  # Sort rows.
        df = df[["ATIVO", "DATA COM", "DATA EX", "DATA PAGAMENTO", "VALOR",
                 "TIPO PROVENTO"]]  # Reorder dataframe.
        return df


z = StocksBR()
t = "bbse3"
a = z.table()
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.payments(ticket=t)
'''
z = ReitsBR()
t = "visc11"
a = z.table()
b = z.info(ticket=t)
c = z.price(ticket=t)
d = z.kpi(ticket=t)
e = z.payments(ticket=t)
'''