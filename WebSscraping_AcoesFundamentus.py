"""
Summary.

Payment system individual functions.
All the informations are retrieved from
https://www.fundamentus.com.br/
"""
# -*- coding: utf-8 -*-

import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# Getting the web page content in text format.
'''
The User-Agent request header contains a characteristic string that
allows the network protocol peers to identify the application type,
operating system, software vendor or software version of the
requesting software user agent.
Validating User-Agent header on server side is a common operation
so be sure to use valid browser’s User-Agent string to avoid
getting blocked.
Font: https://go-colly.org/articles/scraping_related_http_headers/
Font: https://stackoverflow.com/questions/68259148/getting-404-error-for-certain-stocks-and-pages-on-yahoo-finance-python
'''
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
    " AppleWebKit/537.36 (KHTML, like Gecko)" +
    "Chrome/71.0.3578.98 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application" +
    "/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",  # Do not track request header.
    "Connection": "close"
    }


def scrap_info_bs(ticket, url_format, file_name):
    """
    Summary.

    Function to retrieve the brazilian stocks scrap info.
    This function run just for one ticket.

    ticket: String. Ticket code on B3.
    url_format: String. URL.
    file_name: String. Link to the CSV output.
    """
    # Creating an empty dataframe. The definitely one.
    df = pd.DataFrame(columns=["DATA COM", "VALOR", "TIPO PROVENTO",
                               "DATA PAGAMENTO", "QTD AÇÕES"])

    soup = BeautifulSoup(requests.get(url_format,
                                      headers=headers)  # , timeout=5)
                         .text, "html.parser")

    # Looking for the web table.
    # In HTML, a table is represented by the tag <table>.
    webtable = soup.find("table")

    # If the ticket doesn't have a table.
    if webtable is None:
        pass
    else:
        # Getting all table rows.
        # In HTML, a row table is represented by the tag <tr>.
        for webtable_row in webtable.tbody.find_all("tr"):
            # Getting all table columns.
            # In HTML, a column table is represented by the tag <td>.
            webtable_column = webtable_row.find_all("td")
            if webtable_column:  # if webtable_columns != []:
                data_com = webtable_column[0].text.strip(" ")
                valor = webtable_column[1].text.strip(" ")
                tipo_provento = webtable_column[2].text.strip(" ")
                data_pagamento = webtable_column[3].text.strip(" ")
                quantidade_acoes = webtable_column[4].text.strip(" ")
                df = pd.concat(
                    [df, pd.DataFrame.
                     from_records([{"DATA COM": data_com,
                                    "VALOR": valor,
                                    "TIPO PROVENTO": tipo_provento,
                                    "DATA PAGAMENTO": data_pagamento,
                                    "QTD AÇÕES": quantidade_acoes
                                    }]
                                  )], ignore_index=True)

        # Removing rows without payment date.
        df = df[df["DATA PAGAMENTO"] != "-"]

        # Numbers adjustments.
        df["VALOR"] = df["VALOR"].str.replace(".", "")
        df["VALOR"] = df["VALOR"].str.replace(",", ".")

        # Changing data types.
        df["DATA COM"] = pd.to_datetime(df["DATA COM"], format="%d/%m/%Y",
                                        errors="coerce")
        df["DATA COM"] = df["DATA COM"].astype(str)
        df["DATA PAGAMENTO"] = pd.to_datetime(df["DATA PAGAMENTO"],
                                              format="%d/%m/%Y",
                                              errors="coerce")
        df = df.astype({"QTD AÇÕES": int})
        df = df.astype({"VALOR": float})

        # Columns adjustments.
        df["TIPO PROVENTO"] = df["TIPO PROVENTO"].str.upper()
        df["VALOR"] = df["VALOR"]/df["QTD AÇÕES"]

        # Necessary rows.
        df = df[df["VALOR"] > 0]

        # New columns.
        df["TIPO ATIVO"] = "AÇÃO"
        df["ATIVO"] = str.upper(ticket)

        # Reorder dataframe.
        df = df[["ATIVO", "TIPO ATIVO", "DATA COM", "DATA PAGAMENTO", "VALOR",
                 "TIPO PROVENTO"]]

        # Exporting as CSV.
        df.to_csv(file_name, index=False, sep=";", encoding="UTF-8")

        # -*- Graphics -*-
        # Dividends paied per ticket.
        plt.title("PROVENTOS RECEBIDOS POR " + str.upper(ticket))
        plt.plot(df["DATA PAGAMENTO"], df["VALOR"], label=str.upper(ticket))
        plt.ylabel("VALOR (R$)")
        plt.xlabel("ANO")
        # plt.legend()
        plt.show()

        # Dividends paied per year per ticket.
        df_anual = df.set_index("DATA PAGAMENTO")
        dividendos = (df_anual['VALOR']).resample("YE").sum()
        plt.plot(dividendos.index.year[:-1], dividendos[:-1],
                 label=str.upper(ticket))
        plt.title("PROVENTOS ANUAIS RECEBIDOS POR " + str.upper(ticket))
        plt.ylabel("VALOR (R$)")
        plt.xlabel("ANO")
        # plt.legend()
        plt.show()


def brazilian_stocks(ticket):
    """
    Summary.

    Function to set the brazilian stocks parameters.
    Single ticket.
    """
    url_format = ("https://www.fundamentus.com.br/proventos.php?" +
                  "tipo=2&papel={}")
    url_format = url_format.format(ticket)

    return scrap_info_bs(ticket, url_format,
                         "PROVENTOS_" + str.upper(ticket) + ".csv")


brazilian_stocks("bbse3")
