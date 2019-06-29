import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import pandas_datareader.data as web
from f_date import sortable_symbol  # compare_calendar

#-----------------------------------------------------------------------------------------------------------------------

# Given a pathname to a csv file and a list of columns which should be treated as dates
# Return the pandas dataframe containing the data
def read_dataframe(pathname, date_columns=['DateTime']):
    df = pd.read_csv(pathname, parse_dates=date_columns)
    return df

# Given dataframe and pathname of output csv file
# Write dataframe to csv file
def write_dataframe(df, pathname, myindex=False):
    df.to_csv(pathname, index=myindex)
    return

# Given dataframe and column_name and indicator of whether or not to sort results and (optional) sort compare_function
# Return list of UNIQUE values in specified column (sorted if do_sort is True)
def df_get_unique(df, column_name, do_sort=True, key_function=None): # compare_function=None):
    g = df.groupby(column_name).groups
    keys = g.keys()
    if do_sort:
        if key_function == None:
            return sorted(keys)
        else:
            #return sorted(keys, key=compare_function)
            return sorted(keys, key=lambda x: key_function(x))
            #return sorted(keys, compare_function)
    else:
        return keys

"""
# Given dataframe
# 
def df_get_unique_dates(df):
    unique_dates = []
    for dt in hist[symbol].keys():
        dateonly = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
        if not dateonly in unique_dates:
            unique_dates.append(dateonly)
    return unique_dates
"""

# Given dataframe
# Return list of (unique) symbols sorted by their calendar dates
def df_get_sorted_symbols(df, symbol_column='Symbol'):
    #g = df.groupby('Symbol').groups
    #keys = g.keys()
    #sorted_symbols = sorted(keys, compare_calendar)
    sorted_symbols = df_get_unique(df, symbol_column, do_sort=True, key_function=sortable_symbol)
    return sorted_symbols

# Given dataframe and start/end datetime values
# Return the dataframe filtered to contain only rows in datetime range (startdate <= DateTime < enddate)
def df_filter_dates(df, dt0, dt1):
    dfx = df[df['DateTime'] >= dt0]
    dfx = dfx[dfx['DateTime'] < dt1]
    return dfx

# Given dataframe and column_name
# Print summary statistics about the given column's data
def df_print_summary_stats(df, column_name):
    fmt = "0.2f"
    print()
    print(column_name.upper())
    print("min:", format(df[column_name].min(), fmt))
    print("max:", format(df[column_name].max(), fmt))
    print("mean:", format(df[column_name].mean(), fmt))
    print("median:", format(df[column_name].median(), fmt))
    print("stddev:", format(df[column_name].std(), fmt))
    #print "mode:"
    #print df[col].mode()
    #print "quantile:"
    #print df[col].quantile([0.25, 0.75])
    return

# Given a full dataset and a subset of the full dataset
# Return a list of df_subset rows where the rows are contiguous ranges
def get_ranges_df(df_full, df_subset):
    df_rows = []
    dt1 = None
    dt2 = None
    for ix, r in df_subset.iterrows():
        if dt1 == None:
            dt1 = r.DateTime
        else:  # dt2 == None:
            dt2 = r.DateTime

        if dt1 != None and dt2 != None:
            dfx = df_full[(df_full.DateTime >= dt1) & (df_full.DateTime <= dt2)]
            dfy = df_subset[(df_subset.DateTime >= dt1) & (df_subset.DateTime <= dt2)]
            nx = dfx.shape[0]
            ny = dfy.shape[0]
            if nx == ny:
                pass
            else:
                df_rows.append(dfy.iloc[0:dfy.shape[0] - 1].copy())
                dt1 = dt2
                dt2 = None
    if dt1 != None and dt2 == None:
        df_rows.append(df_subset[df_subset.DateTime >= dt1])
    return df_rows

# Given a dataframe of 1-minute data and the session open/close times, calculate the Open,High,Low,Close for each day
def get_ohlc(df, session_open='08:30:00', session_close='15:00:00'):
    df['just_date'] = df['DateTime'].dt.date
    unique_dates = df['just_date'].unique()
    rows = []
    for dt in unique_dates:
        (hh, mm, ss) = parse_timestr(session_open)
        dt1 = datetime(dt.year, dt.month, dt.day, hh, mm, ss)
        (hh, mm, ss) = parse_timestr(session_open)
        dt2 = datetime(dt.year, dt.month, dt.day, hh, mm, ss)
        dfx = df[(df.DateTime > dt1) & (df.DateTime <= dt2)]
        xopen = dfx.iloc[0]['Open']
        xhigh = dfx.High.max()
        xlow = dfx.Low.min()
        xclose = dfx.iloc[dfx.shape[0] - 1]['Close']
        rows.append([dt, xopen, xhigh, xlow, xclose])
    return pd.DataFrame(rows, columns=['DateTime', 'Open', 'High', 'Low', 'Close'])


