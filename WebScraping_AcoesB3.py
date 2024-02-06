"""
Summary.

Code to extract the dividend table of a specific asset using the B3 API.
"""
# -*- coding: utf-8 -*-

import requests
from base64 import b64encode
from pandas import DataFrame as pd_df


class Payments:
    """
    Summary.

    This function get the assets trading name.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_b3_trading_name(asset):
        """
        Summary.

        Function to retrieve the trading name.

        asset: String. Ticket code on B3.
        """
        # Create parameters.
        parameters = {"language": "pt-br",
                      "pageNumber": 1,
                      "pageSize": 20,
                      "company": asset}

        # Convert parameters to bytes for base64 encoding.
        parameters = bytes(str(parameters), encoding="ascii")
        parameters = b64encode(parameters)  # Encode to bytes format.
        parameters = parameters.decode()  # Bytes to string conversion.

        # Request the parameters.
        r = requests.get(r"https://sistemaswebb3-listados.b3.com.br/"
                         "listedCompaniesProxy/CompanyCall/"
                         "GetInitialCompanies/" + parameters)

        # Return the trading name of the company.
        for result in r.json()["results"]:
            if result["issuingCompany"].lower() == asset.lower():
                return result["tradingName"].replace("/", "").replace(".", "")

    @staticmethod
    def get_dividends(asset):
        """
        Summary.

        Function to retrieve dividend table.

        asset: String. Ticket code on B3.
        """
        # Find the trading name of the company.
        trading_name = Payments.get_b3_trading_name(asset)

        # Create parameters with the trading name.
        parameters = {"language": "pt-br",
                      "pageNumber": 1,
                      "pageSize": 99,
                      "tradingName": trading_name}

        # Encode the parameters in base64.
        parameters = bytes(str(parameters), encoding="ascii")
        parameters = b64encode(parameters)
        parameters = parameters.decode()

        r = requests.get(r"https://sistemaswebb3-listados.b3.com.br/"
                         "listedCompaniesProxy/CompanyCall/"
                         "GetListedCashDividends/" + parameters)

        return r.json()["results"]


asset_name = "BBAS"
df = pd_df(Payments.get_dividends(asset_name))

# Exporting as CSV.
df.to_csv("PROVENTOS_" + str.upper(asset_name) + ".csv", index=False, sep=";",
          encoding="UTF-8")

print(df)
