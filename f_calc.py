import math

# Return the calculated quartile value
# Given the mean of the values
# Given the standard deviation of the values
# Given a quartile identifier i (-4, -3, -2, -1, 0, +1, +2, +3, +4) and mean and standard deviation
# Given the decimal places to round (default=4)
def Calc_Quartile(mean, std, i, round_places=4):
    qvalue = (std / 100.0 * mean) / 4.0
    return round(mean + i * qvalue, round_places)

# Return ALL the quartiles (including 'unchanged' = 9 total) in both DICTIONARY and LIST form
# Given the mean of the value
# Given the standard deviation of the value
# Given the decimal places to round (default=4)
def Calc_Quartiles(prev_underlying_close, std, round_places=4):
    Quartiles = ['d4','d3','d2','d1','unch','u1','u2','u3','u4']
    dict_Q = {}
    list_Q = []
    for xi in range(-4, 5):
        quartile = Calc_Quartile(prev_underlying_close, std, xi, round_places)
        list_Q.append(quartile)
        dict_Q[xi] = quartile
    return (list_Q, dict_Q)

# Return the Standard Deviation (std)
# Given the previous implied volatility close (i.e. VIX for ES)
def Calc_Std(prev_implied_vol_close):
    std = float(prev_implied_vol_close) / math.sqrt(252)                    # calculate standard deviation
    return std

