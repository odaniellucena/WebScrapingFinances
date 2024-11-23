"""
Summary.

Retrieve the companies infos from Dividend Investor website.
"""
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods

from bs4 import BeautifulSoup
import requests
import pandas as pd

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


class StocksReitsETFs:
    """
    Summary.

    Retrieve the stocks, reits and ETFs companies infos.
    """

    def __init__(self, ticket):
        self.ticket = ticket
        url = "https://dividendinvestor.com/dividend-history-detail/{}"
        self.url = url.format(ticket.lower())

    def _get_soup(self):
        url = self.url
        page = requests.get(url, headers=headers, timeout=None)
        soup = BeautifulSoup(page.text, "html.parser")  # Getting HTML.
        # Checking if asset exist.
        if (page.status_code != 200 or
            soup.find("table", {"id": "dividends"}) is None or
            soup.find_all(string="No Symbol Found") or
            soup.find_all(string=lambda text: text and
                          "No dividends retrieved for" in text)):
            raise ValueError("Info does not exist")
        return soup

    def _parse_table_payment(self, soup):
        # Table.
        webtable = soup.find("table", {"id": "dividends"})
        tmp = []
        for webtable_row in webtable.find_all("tr"):
            webtable_column = webtable_row.find_all("td")
            # Looking for the rows who have just 6 columns.
            if len(webtable_column) == 6:
                data_com = webtable_column[1].text.strip()[:13]
                data_pagamento = webtable_column[3].text.strip()[:13]
                valor = webtable_column[5].text.strip()
                tmp.append({"TIPO PROVENTO": "DIVIDENDO",
                            "DATA COM": str.strip(data_com),
                            "DATA PAGAMENTO": str.strip(data_pagamento),
                            "VALOR": str.strip(valor)
                            })
        table = pd.DataFrame(tmp)  # Temporary dataframe.
        return table

    def payments(self):
        """
        Summary.

        Function to retrieve the stocks, reits and ETFs payments info.
        """
        soup = self._get_soup()
        df = self._parse_table_payment(soup)  # Table info.
        tmp = ["DATA COM", "DATA PAGAMENTO"]
        for column in tmp:
            df[column] = df[column].str.replace("N/AN/A", "")

        df = df[df["DATA COM"] != ""]
        for column in tmp:
            df[column] = pd.to_datetime(df[column], format="%b. %d, %Y",
                                        errors="coerce").astype(str)

        tmp = ["VALOR"]
        for column in tmp:
            df[column] = pd.to_numeric(df[column], errors="coerce")
            # df = df.astype({column: float})
            # df[column] = round(df[column], 2)

        df = df[df["VALOR"] > 0]  # Necessary rows.
        df["TICKET"] = self.ticket.upper()
        # Reorder dataframe.
        df = df.sort_values(by=["TICKET", "DATA PAGAMENTO"],
                            ascending=[True, False])
        df = df[["TICKET", "DATA COM", "DATA PAGAMENTO", "VALOR"]]
        return df
