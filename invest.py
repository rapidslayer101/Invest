import time, datetime, os, re  # inbuilt

#import yfinance as yf1
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
#from discord_webhook import DiscordWebhook
from forex_python.converter import CurrencyRates, CurrencyCodes
import yahoo_fin.stock_info as yf

from enclib import search


#from twilio.rest import Client
#account_sid = "ACb558feef19198d8ccfe96ca8220dd189"
#auth_token = "10cde7f7f64ada3f43c90a4d721bd1ac"
#client = Client(account_sid, auth_token)

# LOGGING #

start_time = time.time()
start_time_standard = datetime.now()

if not os.path.exists(f"output/logs.txt"):
    os.mkdir("output")
with open(f"output/logs.txt", "w") as f:
    f.write("")


def log(text):
    print(text)
    with open("output/logs.txt", "a+", encoding="utf-8") as f:
        try:
            write = f"{str(datetime.now())[:-4]} RUNTIME: {round(time.time() - start_time, 2):.2f} | {text}\n"
            f.write(write)
        except:
            write = f"{str(datetime.now())[:-4]} RUNTIME: {round(time.time() - start_time, 2):.2f} | PRINTING ERROR\n"
            f.write(write)


# SETTINGS #

# stocks to watch #
stocks = ["TSLA", "BP"]

# the amount of the stocks you own (shares/dollars)
stocks_own = ["6", ""]
purchase_price = ["2927.66", ""]


# watch live stock price data #
stockwatch = 0

if stockwatch == 1:

    # how often to check stocks list (seconds) #
    checktime = 1           # when market "open"
    checktime_closed = 5    # when market in "POST" or "PRE"

    # how often to check market status (mins) #
    statuscheck = 5

    # how often to check stock change data (seconds) #
    changedatacheck = 320


# CODE START #

def current_profit(current, bought, amount):
    c = CurrencyRates()
    #d = CurrencyCodes()
    output = c.convert("USD", "GBP", float(current))
    profit = ((bought/float(amount)) - output) * float(amount)
    profit = profit - profit*2
    print((bought+profit))
    percent = ('{0:.2f}%'.format((bought+profit / bought * 100)))
    print(percent)
    log(f"Profit of: {profit} {percent}")


#def text(user, message):
#    message = client.messages.create(to="+447597299247", from_="+15155188444", body="EXAMPLE TEXT")


log("Bot started with settings:")
log(f"├─> Stocks({len(stocks)}): {stocks}")
stcounter1 = 0
#try:
for stock in stocks:
    if not stocks_own[stcounter1] == "":
        log(f"│   ├─> Registered owning of {stocks_own[stcounter1]} shares of {stock}")
        if not purchase_price[stcounter1] == "":
            log(f"│   │   └─> Buy price for {stocks_own[stcounter1]}x {stock} at {purchase_price[stcounter1]}")
            current_profit(bought=float(purchase_price[stcounter1]), current=yf.get_live_price(stock), amount=stocks_own[stcounter1])
        else:
            log(f"│   │   └─> Buy price missing, please add in settings")
    stcounter1 += 1
log("│   └─> Total portfolio information:")
log("│       ├─> Buy price:")
log("│       ├─> Current value:")
log("│       └─> Profit:")
#except:
log(f"│   └─> Could not read owned stock information, this is likely due to to a lack of fields in the settings")
if stockwatch == 1:
    log("└─> Stockwatch ON, settings:")
    log(f"    ├─> How often to check live stocks: every {checktime}s")
    log(f"    ├─> How often to check closed stocks: every {checktime_closed}s")
    log(f"    └─> How often to check the current market status: every {statuscheck}m")
if stockwatch == 0:
    log("└─> Stockwatch OFF")


# DEFINING #


def plotgraph(stock, name, readback):
    import numpy as np
    import matplotlib.pyplot as plt

    with open(f'stocks/{stock}/{stock}.txt') as f:
        lines = f.readlines()
        line_st = len(lines) - readback
        print(lines)
        y = np.array([round(float(line.split(", ")[4]), 2) for line in lines[line_st:]])
        x = [x for x in range(len(lines[line_st:]))]
        #x = [line.split(" [")[0][:4] for line in lines[line_st:]]

    y_masked = np.ma.masked_less_equal(y, 1000)

    plt.style.use("dark_background")
    ax1 = plt.figure().add_subplot(111)

    ax1.set_title(f"STOCK: {stock}")
    ax1.set_ylabel("Price £")
    ax1.set_xlabel("Days ago")
    ax1.plot(x, y, c='r', label='share price', linewidth=0.5)
    plt.plot(y_masked, 'g', linewidth=0.5)
    plt.axhline(1000, color='b', linestyle='--', linewidth=0.25)

    plt.savefig(f'stocks/{stock}/{stock}.png', dpi=300)
    plt.close()

    #webhook = DiscordWebhook(url=discord_webhook_url, content=name)
    #with open(f'stocks/{stock}/{stock}.png', "rb") as f:
        #webhook.add_file(file=f.read(), filename=f'{stock}.png')
    #webhook.execute()

# FOLDER CREATION #


log("--------------------------------------------------")
for stock in stocks:
    log(f"Checking directory paths for {stock}")
    if not os.path.exists(f'stocks/{stock}'):
        os.makedirs(f'stocks/{stock}')
        log("└─> Directory missing, now been added")
    else:
        log("└─> Directory present")


# STOCK MARKET INFORMATION #


def market_status():
    log("--------------------------------------------------")
    stock_market_status = yf.get_market_status()

    if stock_market_status == "PRE":
        stock_market_status = "PRE-MARKET"
        loopchecks = 1

    if stock_market_status == "PREPRE":
        stock_market_status = "CLOSED (pepe)"
        loopchecks = 0

    if stock_market_status == "CLOSED":
        loopchecks = 0

    if stock_market_status == "POSTPOST":
        stock_market_status = "CLOSED (popo)"
        loopchecks = 0

    if stock_market_status == "POST":
        stock_market_status = "POST-MARKET"
        loopchecks = 2

    if stock_market_status in ["REGULAR", "OPEN"]:
        stock_market_status = "OPEN"
        loopchecks = 3

    log(f"Stock market is currently: {stock_market_status}")

    # loopchecks status codes #
    # -1 = code has not checked the status yet
    # 0 = closed, no checks
    # 1 = pre, some checks
    # 2 = post, some checks
    # 3 = open, all checks
    log(f"LOOPCHECK STATUS CODE: {loopchecks}")
    log(f"CURRENT TIME: {str(datetime.now())[:-4]}")
    log("--------------------------------------------------")
    return loopchecks


loopchecks = -1  # default status code in-case of status retrieval failure
loopchecks = market_status()


# CHECKING OLD STOCK DATA #


log("Collecting old stock data")
date = datetime.now()

date_1d = date - timedelta(days=10)
date_1d = str(date_1d)[:10]

date_begin = date - timedelta(weeks=2609)
date_begin = str(date_begin)[:10]

date = str(date)[:10]


def data_collect(start_date, end_date, stock, run):
    stockdata = yf.get_data(start_date=start_date, end_date=end_date, ticker=stock, interval="1d")
    with open(f"stocks/{stock}/{stock}.txt", "w") as f:
        [f.write(f'{search(str(stockdata.loc[rname]), "Name: ", ", dtype")} '
                 f'{str(list(stockdata.loc[rname])[:-1])}\n') for rname in stockdata.index]

    #while True:
    #    datacollect_go += 1
    #    #dt = stockdata_1d[0].values[datacollect_go]
    #    f.write(f"{round(stockdata_1d['close'].values[datacollect_go],2)}\n")
    #except:
    #    if run == len(stocks):
    #        log(f"└─> {stock} data successfully collected from {start_date} to {end_date}, total entries {datacollect_go-1}")
    #    else:
    #        log(f"├─> {stock} data successfully collected from {start_date} to {end_date}, total entries {datacollect_go-1}")


update_stocks = True

if update_stocks:
    run = 0
    for stock in stocks:
        run += 1
        #datacollect(start_date=date_1d, end_date=date, stock=stock, run=run) # data collect 1d
        data_collect(start_date=date_begin, end_date=date, stock=stock, run=run)  # data collect 1d all
        #print(yf.get_stats(stock))
        #print(yf.get_quote_data(stock))

    log("Finished collecting stock data")

# CHECKING LIVE STOCKS #

if stockwatch == 1:

    if loopchecks in range(0, 3):
        log("getting close prices...")

    for stock in stocks:
        with open(f"stocks/{stock}/{stock}.txt", "w") as f:
            f.write("")

    go = 0
    while True:
        go += 1
        stockwatchinfo = ""
        for stock in stocks:
            stockdata = str(yf.get_quote_data(stock))

            # current price
            m = re.search("'regularMarketPrice':(.+?), 'regularMarketDayHigh'", stockdata)
            if m:
                current = float(m.group(1))
            else:
                current = yf.get_premarket_price(stock)

            # current profit
            m = re.search("'regularMarketChange':(.+?), 'regularMarketChangePercent'", stockdata)
            if m:
                open_change = round(float(m.group(1)), 2)
            else:
                open_change = 0

            # current % change
            m = re.search("'regularMarketChangePercent':(.+?), 'regularMarketTime'", stockdata)
            if m:
                open_change_percent = round(float(m.group(1)), 2)
            else:
                open_change_percent = 0

            if loopchecks == 3:
                with open(f"stocks/{stock}/{stock}.txt", "a+") as f:
                    f.write(f"{current:.2f} {go} {str(datetime.now())[:-4]} OPEN\n")

            if go % changedatacheck == 0:
                plotgraph(stock=stock, name=f"{stock} live [time period]", readback=30)

            stockwatchinfo = f"{stockwatchinfo}{stock} {current:.2f} {open_change:.2f} {open_change_percent:.2f}% "

        log(f"{stockwatchinfo}  {str(datetime.now())[:-4]}")

        if go * checktime / 60 % statuscheck == 0:
            loopchecks = market_status()

        if loopchecks in range(0, 3):
            break

        time.sleep(checktime)

    if loopchecks in range(0, 3):
        log("getting latest prices...")
        go_closed = 0
        while True:
            go_closed = go_closed + 1
            stockwatchinfo_closed = ""
            try:
                for stock in stocks:
                    # pre market
                    if loopchecks == 1:
                        stockdata = str(yf.get_quote_data(stock))

                        # current_closed price
                        m = re.search("'preMarketPrice':(.+?), 'regularMarketChange'", stockdata)
                        if m:
                            current_closed = float(m.group(1))
                        else:
                            current_closed = yf.get_premarket_price(stock)

                        # current profit
                        m = re.search("'preMarketChange':(.+?), 'preMarketChangePercent'", stockdata)
                        if m:
                            closed_change = round(float(m.group(1)), 2)
                        else:
                            closed_change = 0

                        # current % change
                        m = re.search(", 'preMarketChangePercent':(.+?), 'preMarketTime'", stockdata)
                        if m:
                            closed_change_percent = round(float(m.group(1)), 2)
                        else:
                            closed_change_percent = 0

                    # post market
                    if loopchecks == 2:
                        stockdata = str(yf.get_quote_data(stock))

                        # current_closed price
                        m = re.search("'postMarketPrice':(.+?), 'regularMarketChange'", stockdata)
                        if m:
                            current_closed = float(m.group(1))
                        else:
                            current_closed = yf.get_premarket_price(stock)

                        # current profit
                        m = re.search("'regularMarketChange':(.+?), 'regularMarketChangePercent'", stockdata)
                        if m:
                            closed_change = round(float(m.group(1)), 2)

                        # current % change
                        m = re.search("'regularMarketChangePercent':(.+?), 'regularMarketTime'", stockdata)
                        if m:
                            closed_change_percent = round(float(m.group(1)), 2)

                    with open(f"stocks/{stock}/{stock}.txt", "a+") as f:
                        f.write(f"{current_closed:.2f} {go_closed} {str(datetime.now())[:-4]} POST\n")

                    if go_closed % changedatacheck/5 == 0:
                        plotgraph(stock=stock, name=f"{stock} closed", readback=30)

                    stockwatchinfo_closed = f"{stockwatchinfo_closed}{stock} {current_closed:.2f} {closed_change} {closed_change_percent}% "
                log(f"{stockwatchinfo_closed}  {str(datetime.now())[:-4]}")
            except:
                loopchecks = market_status()

            if go_closed * checktime_closed / 60 % statuscheck == 0:
                loopchecks = market_status()

            if loopchecks == 0:
                break

            time.sleep(checktime_closed)

    log("checking stopped, the stock market has no new data to read")

stock = "TSLA"
plotgraph(stock=stock, name=f"{stock} closed", readback=500)

log("--------------------------------------------------")
log(f"SCRIPT FINISHED EXECUTING AT {str(datetime.now())[:-4]}")
f.close()
#os.startfile(f"output/logs.txt")
