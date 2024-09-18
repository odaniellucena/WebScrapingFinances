# Web Scraping of Companies' Dividend Payments and financial metrics

f you invest your money in the stock market, you already know how important it is to know about financial metrics and dividend values historically paid by companies. This information is very important for making decisions about what to do with that specific asset. Many companies offer the possibility of downloading this information (even if not all of it is shown on the asset page) in spreadsheet format, but others may charge a fee to do so. If you don't want to pay, you can simply copy and paste. The questions are:
- Are you willing to copy and paste data from hundreds of sources?
- You know that this data changes every month, right?

What if we automate this task? The scripts provided are purely written in Python and perform the task of extracting data from the main websites.

---
## StatusInvest.py

Retrieve the companies infos from [Status Invest](https://statusinvest.com.br/) website.

Requirements:
- Python 3.x.
- Libs: Requests, BeautifulSoup, Lxml, Pandas.

Classes:
- StocksBR: Retrieve the brazilian stocks infos.
- ReitsBR: Retrieve the brazilian reits companies infos.
- ETFsBR: Retrieve the brazilian ETF's companies infos.
- StocksReits: Retrieve the stocks and reits companies infos.
- ETFs: Retrieve the ETFs companies infos.

Functions:
- info: Function to retrieve the infos.
- price: Function to retrieve prices infos.
- kpi: Function to retrieve the stocks and reits KPI's kpi's infos.
- table: Function to aggregate the full infos.

Exemple:
```python
z = StocksBR()
t = "wege3"
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
```
---
## Investidor10.py

Retrieve the companies infos from [Investidor 10](https://investidor10.com.br/) website.

Requirements:
- Python 3.x.
- Libs: Requests, BeautifulSoup, Lxml, Pandas.

Classes:
- StocksBR: Retrieve the brazilian stocks companies infos.
- ReitsBR: Retrieve the brazilian reits companies infos.
- ETFsBR: Retrieve the brazilian ETF's companies infos.
- StocksReits: Retrieve the stocks and reits companies infos.
- ETFs: Retrieve the ETFs companies infos.

Functions:
- info: Function to retrieve the infos.
- price: Function to retrieve prices infos.
- kpi: Function to retrieve the stocks and reits KPI's kpi's infos.
- table: Function to aggregate the full infos.

Exemple:
```python
a = etfbr_auxtable()  # Necessary execute first.
b = etf_auxtable()  # Necessary execute first.

z = StocksBR()
t = "bbse3"
a = z.info(ticket=t)
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.table(ticket=t)

z = StocksReits()
t = "o"
a = z.info(ticket=t, type_asset="REIT")
b = z.price(ticket=t, type_asset="REIT")
c = z.kpi(ticket=t, type_asset="REIT")
d = z.table(ticket=t, type_asset="REIT")
```
---
## Fundamentus.py

Retrieve the companies infos from [Fundamentus](https://www.fundamentus.com.br/) website.

Requirements:
- Python 3.x.
- Libs: Requests, BeautifulSoup, Timedelta, Pandas.

Classes:
- StocksBR: Retrieve the brazilian stocks companies infos.
- ReitsBR: Retrieve the brazilian reits companies infos.

Functions:
- price: Function to retrieve prices infos.
- kpi: Function to retrieve the stocks and reits KPI's kpi's infos.
- table: Function to aggregate the full infos.
- payments: Function to retrieve the payments info.

Exemple:
```python
a = etfbr_auxtable()  # Necessary execute first.
b = etf_auxtable()  # Necessary execute first.

z = StocksBR()
t = "bbse3"
a = z.table()
b = z.price(ticket=t)
c = z.kpi(ticket=t)
d = z.payments(ticket=t)
```
---
## YahooFinance.py

Retrieve the companies infos from [Yahoo Finances](https://br.financas.yahoo.com) website.

Requirements:
- Python 3.x.
- Libs: Yfinance, Pandas.

Classes:
- AllTypeAssets: Retrieve the stocks, reits and ETF's companies infos.

Functions:
- info: Function to retrieve all kind of assets infos.
- price: Function to retrieve all kind of assets prices infos.
- kpi: Function to retrieve all kind of assets kpi's infos.
- table: Function to aggregate all kind of assets full infos.
- payments: Function to retrieve all kind of assets payments infos.

Exemple:
```python
z = AllTypeAssets()

t = "wege3"
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
```
---
## DividendInvestor.py

Retrieve the companies infos from [Dividend Investor](https://www.dividendinvestor.com/) website.

Requirements:
- Python 3.x.
- Libs: Requests, BeautifulSoup, Lxml, Pandas.

Classes:
- StocksReitsETFs: Retrieve the stocks, reits and ETF's companies infos.

Functions:
- payments: Function to retrieve the payments info.

Exemple:
```python
z = StocksReitsETFs()
t = "msft"
d = z.payments(t)
```
---
## ExchangeRate.py

Exchange rate extracted from Brazil central bank.

Requirements:
- Python 3.x.
- Libs: Requests, Date, Timedelta, Pandas.

Functions:
- ptax_bcb: Function to access BCB open data API.
- ptax_today_bcb: Function to access BCB open data API to get current price a currency.
- ptax_today: Function to access Awesomeapi API to get current price a currency.

Exemple:
```python
a = ptax_bcb(StartDate="01-01-2018", Currency="USD")
b = ptax_today_bcb(Currency="USD")
c = ptax_today(Currency="USD-BRL")
```
---
## KPIsRF.py

Exchange rate function.

Requirements:
- Python 3.x.
- Libs: Pandas, Numpy.

Functions:
- cdi_annually: Function to access BCB open data API.
- cdi_annually_today: Function to access BCB open data API.

Exemple:
```python
a = cdi_annually()
b = cdi_annually_today()
```