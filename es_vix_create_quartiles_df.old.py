import sys
import os
from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
import math

#-----------------------------------------------------------------------------------------------------------------------

import f_data_folder as folder
from f_args import *
from f_date import *
from f_file import *
from f_calc import *
from f_dataframe import *
from f_roll_date import *
from f_iqfeed import *

#-----------------------------------------------------------------------------------------------------------------------

def print_trades(trade_column, trade_rows, side, entry_price, exit_price, df_rolls):
    average = 0.0
    for (t_entry, t_exit, cal_adjust, discount_adjust) in trade_rows:
        day_count = (t_exit.Date - t_entry.Date).days
        roll_count = roll_exists_in_date_range(t_entry.Date, t_exit.Date, df_rolls)
        roll_count_indicator = '*' * roll_count
        output = get_output(t_entry, t_exit, cal_adjust, discount_adjust)
        output += roll_count_indicator
        print output
        average += day_count
    average /= len(trades)
    print
    print len(trades), "trades"
    print "average holding period (days): %.1f" % (average)
    return

def write_trades_file(filename, trade_column, trade_rows, side, entry_price, exit_price, df_rolls):
    f = open(folder + filename, 'w')
    f.write("Side,EntryDiscount,ExitDiscount,AdjustDiscount,EntrySpread,ExitSpread,AdjustSpread,EntryDate,ExitDate,HoldingDays,RollCount\n")
    for (t_entry, t_exit, cal_adjust, discount_adjust) in trade_rows:
        day_count = (t_exit.Date - t_entry.Date).days
        roll_count = roll_exists_in_date_range(t_entry.Date, t_exit.Date, df_rolls)
        output = get_output(t_entry, t_exit, cal_adjust, discount_adjust)
        output += str(roll_count)
        f.write(output + '\n')
    f.close()
    return

def calc_rolling_mean(df, lookback):
    df['d4'] = df['Qd4'].shift(1).rolling(lookback).mean()
    df['d3'] = df['Qd3'].shift(1).rolling(lookback).mean()
    df['d2'] = df['Qd2'].shift(1).rolling(lookback).mean()
    df['d1'] = df['Qd1'].shift(1).rolling(lookback).mean()
    df['unch'] = df['Qunch'].shift(1).rolling(lookback).mean()
    df['u1'] = df['Qu1'].shift(1).rolling(lookback).mean()
    df['u2'] = df['Qu2'].shift(1).rolling(lookback).mean()
    df['u3'] = df['Qu3'].shift(1).rolling(lookback).mean()
    df['u4'] = df['Qu4'].shift(1).rolling(lookback).mean()
    return

################################################################################

print "Calculating quartiles for ES using VIX.XO to determine standard deviation"
print "Output file will be comma-delimeted pandas-ready dataframe (.csv)"
print

project_folder = join(data_folder, "vix_es")

#dt1 = datetime(2017, 1, 1)
#dt2 = datetime.now()
#df = get_historical_contract("@ES#", dt1, dt2)
#df.to_csv("@ES# (Daily).csv", index=False)
#df = get_historical_contract("VIX.XO", dt1, dt2)
#df.to_csv("VIX.XO (Daily).csv", index=False)



filename1 = "@ES# (Daily).csv"
filename2 = "VIX.XO (Daily).csv"
filename3 = "@VX_contango.csv"

lookback_days = 5
output_filename = "es_vix_quartiles ({0}-day lookback).DF.csv".format(lookback_days)

print "project folder:", quoted(project_folder)
print "input files:", quoted(filename1), quoted(filename2), quoted(filename3)
print "lookback days:", lookback_days
print

print "----------BEGIN CALCULATIONS----------"

df1 = read_dataframe(join(project_folder, filename1))
df2 = read_dataframe(join(project_folder, filename2))
df3 = read_dataframe(join(project_folder, filename3))

df1 = df1.drop(['High', 'Low'], 1)
df2 = df2.drop(['High', 'Low', 'Volume'], 1)
df3 = df3.drop(['Open_x', 'Close_x', 'Open_y', 'Close_y', 'Open', 'Close'], 1)

df = pd.merge(df1, df2, on=['DateTime'])
df = pd.merge(df, df3, on=['DateTime'])

df.rename(columns={'Symbol_x':'Symbol_ES', 'Open_x':'Open_ES', 'Close_x':'Close_ES', 'Volume':'Volume_ES', 'Open_y':'Open_VIX', 'Close_y':'Close_VIX', 'Symbol_y':'Symbol_VX', 'Volume_x':'Volume_VX1', 'Volume_y':'Volume_VX2', 'Contango_Open':'Open_Contango', 'Contango_Close':'Close_Contango'}, inplace=True)

# Output this daily VIX/ES summary data (for potential analysis or debugging)
summary_filename = "es_vix_daily_summary.DF.csv"
write_dataframe(df, join(project_folder, summary_filename))
print
print "VIX/ES summary (daily data) output to file:", quoted(summary_filename)
print

symbols = df_get_sorted_symbols(df, 'Symbol_ES')            # get list of unique ES symbols in our data

rows = []                                                   # store our row tuples here (they will eventually be used to create a dataframe)

# For each specific ES symbol, perform our quartile calculations
for es in symbols:  # symbols[-2:]: 
    print "Processing future:", es
    df_es = read_dataframe(get_df_pathname(es))
    dfx = df[df.Symbol_ES == es]
    for (ix,row) in dfx.iterrows():
        if not (ix+1) in dfx.index:                         # if we are at the end of the dataframe rows (next row doesn't exist)
            continue
        
        # Use Close of ES and VIX
        es_close = row['Close_ES']                          # ES close
        vix_close = row['Close_VIX']                        # VIX close
        #std = vix_close / math.sqrt(252)                    # calculate standard deviation
        std = round(Calc_Std(vix_close), 4)
        dt_prev = row['DateTime']                           # date of ES/VIX close to use
        dt = dfx.loc[ix+1].DateTime                         # following date (of actual quartile calculation)

        # Get the ES 1-minute bars for the day session (for date following date of ES/VIX close)
        exchange_open = dt.replace(hour=8, minute=30)
        exchange_close = dt.replace(hour=15, minute=0)
        df_day = df_es[(df_es.DateTime > exchange_open) & (df_es.DateTime <= exchange_close)]   # ES 1-minute bars for day session
        day_open = df_day.iloc[0]['Open']
        day_high = df_day.High.max()
        day_low = df_day.Low.min()
        row_count=df_day.shape[0]
        day_close = df_day.iloc[row_count-1]['Close']

        # For each quartile, determine if it was hit during the day session of ES
        hit_quartile = {}
        #print es_close, std
        (q_list, q_dict) = Calc_Quartiles(es_close, std)
        for i in range(+4, -5, -1):
            #quartile = Quartile(es_close, std, i)       # for the given close price and standard dev, calculate the quartiles
            #quartile = round(quartile, 4)
            quartile = q_dict[i]
            if day_low <= quartile and day_high >= quartile:
                hit_quartile[i] = 1
            else:
                hit_quartile[i] = 0
            #print i, quartile, hit_quartile[i]
            
        rows.append((dt, es, es_close, vix_close, std, day_open, day_high, day_low, day_close, hit_quartile[-4], hit_quartile[-3], hit_quartile[-2], hit_quartile[-1], hit_quartile[0], hit_quartile[1], hit_quartile[2], hit_quartile[3], hit_quartile[4]))

df_new = pd.DataFrame(rows, columns=['DateTime', 'Symbol_ES', 'Prev_Close_ES', 'Prev_Close_VIX', 'Std', 'SessionOpen_ES', 'SessionHigh_ES', 'SessionLow_ES', 'SessionClose_ES', 'Qd4', 'Qd3', 'Qd2', 'Qd1', 'Qunch', 'Qu1', 'Qu2', 'Qu3', 'Qu4'])        
#df_new = pd.DataFrame(rows, columns=['DateTime', 'Symbol_ES', 'Close_ES', 'Std', 'Qd4', 'Qd3', 'Qd2', 'Qd1', 'Qunch', 'Qu1', 'Qu2', 'Qu3', 'Qu4'])
# df_new = df_new.set_index(['some_col1', 'some_col2'])       # Possibly also this if these can always be the indexes

calc_rolling_mean(df_new, lookback_days)

calc_days_to_quartile_hit = False
if calc_days_to_quartile_hit:
    # Create columns that will hold the number of days until a quartile hit occurs
    undef_value = -1
    df_new['days_to_d4'] = undef_value
    df_new['days_to_d3'] = undef_value
    df_new['days_to_d2'] = undef_value
    df_new['days_to_d1'] = undef_value
    df_new['days_to_unch'] = undef_value
    df_new['days_to_u1'] = undef_value
    df_new['days_to_u2'] = undef_value
    df_new['days_to_u3'] = undef_value
    df_new['days_to_u4'] = undef_value

    print "\nIterating dataframe rows to determine actual days-to-hit numbers for each quartile . . .",

    # Now scan dataframe rows to determine how many days until each specific quartile is ACTUALLY hit
    for (ix,row) in df_new.iterrows():
        if ix % 100 == 0:
            print '.',
        if np.isnan(row['unch']):
            continue
        dt = row['DateTime']

        for col in ['d4', 'd3', 'd2', 'd1', 'unch', 'u1', 'u2', 'u3', 'u4']:
            qcol = "Q" + col
            dayscol = "days_to_" + col
            dfx = df_new[(df_new[qcol] == 1) & (df_new.DateTime >= dt)]
            # An empty dataframe means there were no rows where the specified quartile was hit that satisfied the date constraint
            if not dfx.empty:
                ix_hit = dfx.index[0]
                df_new.set_value(ix, dayscol, ix_hit-ix)
    print



write_dataframe(df_new, join(project_folder, output_filename))

print
print "Quartile analysis output to file:", quoted(output_filename)
print




