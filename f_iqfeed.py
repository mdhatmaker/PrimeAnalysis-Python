from iqapi import historicData
import pandas as pd
import numpy as np
from os.path import join
from datetime import datetime, timedelta


#-------------------------------------------------------------------------------

from f_data_folder import *
from f_date import *

#-------------------------------------------------------------------------------

INTERVAL_DAILY = 0
INTERVAL_MINUTE = 60
INTERVAL_HOUR = 3600


# Given an interval value (in seconds--or zero for DAILY)
# Return a string representing that interval (for use in a filename, for instance)
def strinterval(interval):
    if interval == INTERVAL_DAILY:
        return "daily"
    elif interval == INTERVAL_MINUTE:
        return "minute"
    elif interval == INTERVAL_HOUR:
        return "hour"
    else:
        return str(interval)
    
# Given an IQFeed symbol and the start/end dates and interval in seconds (0=daily) and begin/end filter time ("HHmmSS")
# Return a dataframe containing the historical data for this symbol (using IQFeed)
def get_historical(symbol, dateStart, dateEnd, interval=INTERVAL_DAILY, beginFilterTime='', endFilterTime=''):
    iq = historicData(dateStart, dateEnd, interval, beginFilterTime, endFilterTime)
    df = iq.download_symbol(symbol)
    df['Volume'] = df['Volume'].astype(np.int)
    df['oi'] = df['oi'].astype(np.int)
    return df


# Given a contract symbol and date start/end and interval in seconds (0=daily) and begin/end filter time ("HHmmSS")
# Return a dataframe containing the historical data for this contract (using IQFeed)
def get_historical_contract(symbol, dateStart, dateEnd, interval=INTERVAL_DAILY, beginFilterTime='', endFilterTime=''):
    df = get_historical(symbol, dateStart, dateEnd, interval, beginFilterTime, endFilterTime)
    df = df.reset_index()  # initially, the DateTime is the index
    df.sort_values(["DateTime"], ascending=True, inplace=True)
    return df


# Given a symbol root and a contract month (1-12) and contract year (4-digit)
# Return a dataframe containing the historical data for this futures contract (using IQFeed)
# (optional) days (of data to retrieve) defaults to 365 (1-year)
def get_historical_future(symbol_root, m, y, days=365):
    dateEnd = last_day_of_month(datetime(y, m, 1))
    dateStart = dateEnd - timedelta(days=days)
    mYY = monthcodes[m - 1] + str(y)[-2:]
    symbol = symbol_root + mYY
    # iq = historicData(dateStart, dateEnd, interval_1hour)
    # symbolOneData = iq.download_symbol(symbolOne)
    symbolData = get_historical(symbol, dateStart, dateEnd)
    return symbolData


# Given a symbol root (ex: "@VX") and a starting/ending year (y1/y2)
# create a .CSV file with the symbol root as the name that contains price data for all
#  futures in year range
def create_historical_futures_df(symbol_root, y1, y2, interval=INTERVAL_DAILY):
    df = pd.DataFrame()
    for y in range(y1, y2 + 1):
        for m in range(1, 12 + 1):
            dfx = get_historical_future(symbol_root, m, y)
            if df.shape[0] == 0:
                df = dfx
            else:
                df = df.append(dfx)
    df = df.reset_index()
    # df['Volume'] = df['Volume'].astype(np.int)
    # df['oi'] = df['oi'].astype(np.int)
    df['sort'] = df['Symbol'].apply(lambda x: x[4:6] + x[3])
    df.sort_values(["sort", "DateTime"], ascending=True, inplace=True)
    df.drop(['sort'], axis=1, inplace=True)
    filename = "{0}_futures.{1}.DF.csv".format(symbol_root, strinterval(interval))
    df.to_csv(join(df_folder, filename), index=False)
    return df

def update_historical_futures_df(symbol_root, y1, y2, interval=INTERVAL_DAILY):
    return
