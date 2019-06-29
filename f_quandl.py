import quandl
import json
import pandas as pd
from datetime import datetime, timedelta


#-----------------------------------------------------------------------------------------------------------------------

from f_date import *

#-----------------------------------------------------------------------------------------------------------------------


quandl.ApiConfig.api_key = "gCbpWopzuxctHw6y-qq5"



# Return the Quandl symbol (i.e. "CME/HGH2016") for a given futures instrument
# instrument is Quandl symbol (i.e. "CL")
# mYY is monthcode and 2-digit year (i.e. "X15")
# exchange is Quandl exchange (i.e. "CME", "ICE", ...)
def get_quandl_symbol(instrument, mYY, exchange):
    monthcode = mYY[0]
    year_str = "20" + mYY[1:]
    symbol = exchange + "/" + instrument + monthcode + year_str
    return (monthcode, int(year_str), symbol)

# Return a string in mYYYY format (ex: "N2017")
# Given a string in mYY format (ex: "N17")
def get_mYYYY(mYY):
    monthcode = mYY[0]
    year_str = "20" + mYY[1:]
    return monthcode + year_str

# Return a string that contains the given date in Quandl format (i.e. "2017-2-18")
def qdate(dt):
    return dt.strftime("%Y-%m-%d")

# Return a pandas dataframe containing the Quandl historical data for the specified instrument
# instrument is Quandl symbol (i.e. "CL")
# mYY is monthcode and 2-digit year (i.e. "X15")
# exchange is Quandl exchange (i.e. "CME", "ICE", ...)
def get_futures_data(instrument, mYY, exchange, lookback=timedelta(days=365)):
    (mc1, y1, symbol) = get_quandl_symbol(instrument, mYY, exchange)
    m1 = get_month_number(mc1)
    (m2, y2) = next_month(m1, y1)
    dt2 = datetime(y2, m2, 1)
    dt1 = dt2 - lookback

    dt1_str = qdate(dt1)
    dt2_str = qdate(dt2)
    print symbol, dt1_str, dt2_str
    
    df = quandl.get(symbol, start_date=dt1_str, end_date=dt2_str)
    
    return df

# Return an array of 12 pandas dataframes containing the Quandl historical data for the specified instrument
# instrument is Quandl symbol (i.e. "CL")
# mYY is monthcode and 2-digit year (i.e. "X15")
# exchange is Quandl exchange (i.e. "CME", "ICE", ...)
def get_futures_data_for_year(instrument, year, exchange):
    df_year = [ None, None, None, None, None, None, None, None, None, None, None, None ]
    yy = str(year)[-2:]
    for m in range(1, 12+1):
        monthcode = get_monthcode(m)
        df = get_futures_data(instrument, monthcode + yy, exchange)
        df_year[m-1] = df
    return df_year

def get_calendar_price(data, cal, dt, tm):
    cal1 = cal[0:2]
    cal2 = cal[2:]
    if not (data.has_key(cal1) and data.has_key(cal2)): return (False, 0.0000)
    settle1 = data[cal1].Settle.to_dict()
    settle2 = data[cal2].Settle.to_dict()
    d = get_quandl_date(dt)
    #print d
    if not (settle1.has_key(d) and settle2.has_key(d)): return (False, 0.0000)
    return (True, settle1[d] - settle2[d])

# Return the volatility surface data or volatility model data from the OptionWorks Quandl data
# Given Quandl implied volatility surface instrument symbol (ex: "NYM_CL_CL")
# Given mYY monthcode and 2-digit year (ex: "X15")
# Given the suffix to indicate volatility surface ("IVS") or volatility model ("IVM")
def get_implied_volatility(instrument, mYY, suffix, lookback=timedelta(days=365)):
    (mc1, y1, symbol) = get_quandl_symbol(instrument + "_", mYY, "OWF")
    m1 = get_month_number(mc1)
    (m2, y2) = next_month(m1, y1)
    dt2 = datetime(y2, m2, 1)
    dt1 = dt2 - lookback

    dt1_str = qdate(dt1)
    dt2_str = qdate(dt2)
    print symbol, dt1_str, dt2_str

    #mYYYY = get_mYYYY(mYY)
    #qsymbol = "OWF/" + symbol + "_" + mYYYY + "_IVS"
    qsymbol = symbol + "_" + suffix
    #OWF/NYM_CL_CL_N2019_IVS
    #df = quandl.get(qsymbol, start_date=dt1_str, end_date=dt2_str)
    df = quandl.get(qsymbol)
    return df

# Return the volatility surface data from the OptionWorks Quandl data
# Given Quandl implied volatility surface instrument symbol (ex: "NYM_CL_CL")
# Given mYY monthcode and 2-digit year (ex: "X15")
def get_implied_volatility_surface(instrument, mYY):
    #OWF/NYM_CL_CL_N2019_IVS
    df = get_implied_volatility(instrument, mYY, "IVS")
    return df

# Return the volatility model data from the OptionWorks Quandl data
# Given Quandl implied volatility surface instrument symbol (ex: "NYM_CL_CL")
# Given mYY monthcode and 2-digit year (ex: "X15")
def get_implied_volatility_model(instrument, mYY):
    #OWF/NYM_CL_CL_N2019_IVM
    df = get_implied_volatility(instrument, mYY, "IVM")
    return df


#symbol = "CME/HGK2017-HGM2017"
#data = quandl.get(symbol)                       # get data for symbol
# Change formats
#data = quandl.get(symbol, returns="numpy")      # get data in NumPy array
# Make a filtered time-series call
#data = quandl.get(symbol, start_date="2001-12-31", end_date="2005-12-31")   # get data for date range
#data = quandl.get(["NSE/OIL.1", "WIKI/AAPL.4"]) # get specific columns
#data = quandl.get("WIKI/AAPL", rows=5)          # get last 5 rows
# Preprocess the data
#data = quandl.get("EIA/PET_RWTC_D", collapse="monthly") # change sampling frequency
#data = quandl.get("FRED/GDP", transformation="rdiff")   # perform elementary calculations on the data



#df_go = get_futures_data('G', 'F16', 'ICE')

df_go14 = get_futures_data_for_year('G', 2014, 'ICE')
#df_go15 = get_futures_data_for_year('G', 2015, 'ICE')
#df_go16 = get_futures_data_for_year('G', 2016, 'ICE')
#df_go17 = get_futures_data_for_year('G', 2017, 'ICE')

#df_ho = get_futures_data_for_year('HO', 2016, 'CME')

df1 = get_implied_volatility_surface("NYM_CL_CL", "N17")
df2 = get_implied_volatility_model("NYM_CL_CL", "J18")
print "df1 and df2"

print "Done."

"""
cl_data = {}

get_futures_data_for_year(cl_data, 2015, "CL")
get_futures_data_for_year(cl_data, 2016, "CL")
get_futures_data_for_year(cl_data, 2017, "CL")
"""

"""
########## READ HG DATA AND CONSTRUCT CALENDARS ##########
data = {}

get_calendar_data_for_year(data, 2010)
get_calendar_data_for_year(data, 2011)
get_calendar_data_for_year(data, 2012)
get_calendar_data_for_year(data, 2013)
get_calendar_data_for_year(data, 2014)
get_calendar_data_for_year(data, 2015)
get_calendar_data_for_year(data, 2016)
get_calendar_data_for_year(data, 2017)
"""
