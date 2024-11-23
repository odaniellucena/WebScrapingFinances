# Web Scraping of Companies' Dividend Payments and financial metrics

f you invest your money in the stock market, you already know how important it is to know about financial metrics and dividend values historically paid by companies. This information is very important for making decisions about what to do with that specific asset. Many companies offer the possibility of downloading this information (even if not all of it is shown on the asset page) in spreadsheet format, but others may charge a fee to do so. If you don't want to pay, you can simply copy and paste. The questions are:
- Are you willing to copy and paste data from hundreds of sources?
- You know that this data changes every month, right?

What if we automate this task? The scripts provided are purely written in Python and perform the task of extracting data from the main websites.

---
## status_invest.py

Retrieve the companies infos from [Status Invest](https://statusinvest.com.br/) website.

Requirements:
- Python 3.x.
- Libs: Requests, BeautifulSoup, Lxml, Pandas, Numpy.

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
T = "O"
# z = StocksBR(ticket=T)
# z = ReitsBR(ticket=T)
# z = ETFsBR(ticket=T)
# z = StocksReits(ticket=T, type_asset="STOCKS")
z = StocksReits(ticket=T, type_asset="REITS")
# z = ETFs(ticket=T)

a = z.info()
b = z.price()
c = z.kpi()
d = z.table()
```
---
## investidor_10.py

Retrieve the companies infos from [Investidor 10](https://investidor10.com.br/) website.

Requirements:
- Python 3.x.
- Libs: Requests, BeautifulSoup, Lxml, Pandas, Numpy.

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
# Necessary execute first to execute brazilian and global ETFs.
a = etfbr_auxtable()
b = etf_auxtable()

T = "BBAS3"
z = StocksBR(ticket=T)
#z = ReitsBR(ticket=T)
#z = ETFsBR(ticket=T)
#z = StocksReits(ticket=T, type_asset="STOCKS")
#z = StocksReits(ticket=T, type_asset="REITS")
#z = ETFs(ticket=T)

a = z.info()
b = z.price()
c = z.kpi()
d = z.table()
```
---
## fundamentus.py

Retrieve the companies infos from [Fundamentus](https://www.fundamentus.com.br/) website.

Requirements:
- Python 3.x.
- Libs: Requests, BeautifulSoup, Timedelta, Pandas, Numpy.

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
T = "VIVT3"
x = StocksBR(ticket=T, type_table="KPI")
y = StocksBR(ticket=T, type_table="PAYMENT")
# t = "HGLG11"
# x = ReitsBR(ticket=t, type_table="KPI")
# y = ReitsBR(ticket=t, type_table="PAYMENT")

a = x.table()
b = x.price()
c = x.kpi()
d = y.payments()
```
---
## yahoo_finance.py

Retrieve the companies infos from [Yahoo Finances](https://br.financas.yahoo.com) website.

Requirements:
- Python 3.x.
- Libs: Yfinance, Pandas, Numpy.

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
T = "VT"
z = AllTypeAssets(ticket=T, country=None)

a = z.info()
b = z.price()
c = z.kpi()
d = z.payments(start="2018-01-01")
e = z.table()
```
---
## dividend_investor.py

Retrieve the companies infos from [Dividend Investor](https://www.dividendinvestor.com/) website.

Requirements:
- Python 3.x.
- Libs: Requests, BeautifulSoup, Pandas.

Classes:
- StocksReitsETFs: Retrieve the stocks, reits and ETF's companies infos.

Functions:
- payments: Function to retrieve the payments info.

Exemple:
```python
T = "msft"
z = StocksReitsETFs(ticket=T)
a = z.payments()
```
---
## exchange_rate.py

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
a = ptax_bcb(start_date="01-01-2018", currency="USD")
b = ptax_today_bcb(currency="USD")
c = ptax_today(currency="USD-BRL")
```
---
## KPIsRF.py

Exchange rate function.

Requirements:
- Python 3.x.
- Libs: Pandas.

Functions:
- cdi_annually: Function to access BCB open data API.
- cdi_annually_today: Function to access BCB open data API.

Exemple:
```python
a = cdi_annually()
b = cdi_annually_today()
```