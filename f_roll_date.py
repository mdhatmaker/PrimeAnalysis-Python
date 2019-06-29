from f_date import *

bizday_count_qgc = 1        # business days before expiry (used for roll)
bizday_count_qho = 10       # business days before expiry (used for roll)

# Given a symbol root (ex: '@VX')
# Return a tuple containing roll date function and roll rule description
def get_roll_function(symbol_root):
    sym = symbol_root.strip().upper()
    if sym == '@ES':  # TODO: check if we should continue using VIX roll rule
        roll_description = "Rolling one day prior to first Wed on or before 30 days prior to 3rd Friday of month immediately following expiration month"
        return (get_roll_dates_es, roll_description)
    elif sym == '@JY':
        roll_description = "Rolling one day prior to two business days prior to 3rd Wednesday of delivery month"
        return (get_roll_dates_jy, roll_description)
    elif sym == '@TY':
        roll_description = "Rolling one day prior to seventh business day prior last business day of delivery month"
        return (get_roll_dates_ty, roll_description)
    elif sym == '@VX':
        roll_description = "Rolling one day prior to first Wed on or before 30 days prior to 3rd Friday of month immediately following expiration month"
        return (get_roll_dates_vx, roll_description)
    elif sym == 'QGC':
        roll_description = "Rolling {0} business days before the 3rd-last business day of the expiration month".format(bizday_count_qgc)
        return (get_roll_dates_gc, roll_description)    
    elif sym == 'QHO':
        roll_description = "Rolling {0} business days before the last business day of the expiration month".format(bizday_count_qho)
        return (get_roll_dates_ho, roll_description)    
    else:
        return (None, None)

#-----------------------------------------------------------------------------------------------------------------------
# Calculate @VX expiration
def expiry_date_vx(m1, y1):
    #bizday_count = 10                                   # business days before end of month (used for roll)
    #return last_business_day(m1, y1, bizday_count)      # [bizday_count] business days before end of month
    (mn1, yn1) = next_month(m1, y1)    
    xdt = x_weekday_of_month(mn1, yn1, 3, weekdays['Fri'])  # get the 3rd Friday of the (next) month
    xdt -= timedelta(days=30)                               # 30 days previous
    while xdt.weekday() != weekdays['Wed']:                 # find the first Wed on or before this date
        xdt -= timedelta(days=1)
    return xdt

# Calculate @VX roll date
def roll_date_vx(m1, y1):
    xdt = expiry_date_vx(m1, y1) - BDay(1)                  # roll one business day prior to expiration
    #dt = pd.datetime(y, m, 1)
    #lbd = dt - BDay(1) 
    return xdt

# Return @VX roll dates for given month and previous month
def get_roll_dates_vx(m1, y1):
    (mp1, yp1) = prev_month(m1, y1)
    return (roll_date_vx(mp1, yp1), roll_date_vx(m1, y1))

#-----------------------------------------------------------------------------------------------------------------------
# Ccalculate QHO roll date
def roll_date_ho(m1, y1):
    return last_business_day(m1, y1, bizday_count_qho)      # [bizday_count] business days before end of month

# Return QHO roll dates for given mmonth and previous month
def get_roll_dates_ho(m1, y1):
    (mp1, yp1) = prev_month(m1, y1)
    (mp2, yp2) = prev_month(mp1, yp1)
    return (roll_date_ho(mp2, yp2), roll_date_ho(mp1, yp1))

#-----------------------------------------------------------------------------------------------------------------------
# Calculate @ES (S&P e-mini) expiration
def expiry_date_es(m1, y1):
    #(mn1, yn1) = next_month(m1, y1)
    #xdt = x_weekday_of_month(mn1, yn1, 3, weekdays['Fri'])  # get the 3rd Friday of the (next) month
    xdt = x_weekday_of_month(m1, y1, 3, weekdays['Fri'])    # get the 3rd Friday of the month
    #xdt -= timedelta(days=30)                               # 30 days previous
    while xdt.weekday() != weekdays['Wed']:                 # find the first Wed on or before this date
        xdt -= timedelta(days=1)
    return xdt

# Calculate @ES roll date
def roll_date_es(m1, y1):
    xdt = expiry_date_es(m1, y1) - BDay(1)                  # roll one business day prior to expiration
    #dt = pd.datetime(y, m, 1)
    #lbd = dt - BDay(1)
    return xdt

# Return @ES roll dates for given month and previous month
def get_roll_dates_es(m1, y1):
    if not monthcodes[m1-1] in ['H', 'M', 'U', 'Z']:
        return (None, None)
    (mp1, yp1) = add_month(m1, y1, -3)
    return (roll_date_es(mp1, yp1), roll_date_es(m1, y1))

#-----------------------------------------------------------------------------------------------------------------------
# Calculate QGC (gold) expiration
def expiry_date_gc(m1, y1):
    xdt = last_business_day(m1, y1, 3)                      # 3rd-last business day of month
    #xdt -= BDay(7)                                          # seventh biz day preceding
    return xdt

# Calculate QGC roll date
def roll_date_gc(m1, y1):
    xdt = expiry_date_gc(m1, y1)
    #xdt = expiry_date_gc(m1, y1) - BDay(1)                  # roll one business day prior to expiration
    return xdt

# Return QGC roll dates for given month and previous month
def get_roll_dates_gc(m1, y1):
    (mp1, yp1) = prev_month(m1, y1)
    return (roll_date_gc(mp1, yp1), roll_date_gc(m1, y1))

#-----------------------------------------------------------------------------------------------------------------------
# Calculate @JY (Japanese Yen) expiration
def expiry_date_jy(m1, y1):
    xdt = x_weekday_of_month(m1, y1, 3, weekdays['Wed'])    # get the 3rd Wednesday of the month
    xdt -= BDay(2)                                          # 2nd business day immediately preceding 3rd Wed
    return xdt

# Calculate @JY roll date
def roll_date_jy(m1, y1):
    xdt = expiry_date_jy(m1, y1) - BDay(1)                  # roll 1 business day prior to expiration
    return xdt

# Return @JY roll dates for given month and previous month
def get_roll_dates_jy(m1, y1):
    if not monthcodes[m1-1] in ['H', 'M', 'U', 'Z']:
        return (None, None)
    (mp1, yp1) = add_month(m1, y1, -3)
    return (roll_date_jy(mp1, yp1), roll_date_jy(m1, y1))

#-----------------------------------------------------------------------------------------------------------------------
# Calculate @TY (10-Year T-Note) expiration
def expiry_date_ty(m1, y1):
    xdt = last_business_day(m1, y1)                         # last business day of month
    xdt -= BDay(7)                                          # seventh biz day preceding
    return xdt

# Calculate @TY roll date
def roll_date_ty(m1, y1):
    xdt = expiry_date_ty(m1, y1) - BDay(1)                  # roll one business day prior to expiration
    return xdt

# Return @TY roll dates for given month and previous month
def get_roll_dates_ty(m1, y1):
    if not monthcodes[m1-1] in ['H', 'M', 'U', 'Z']:
        return (None, None)
    (mp1, yp1) = add_month(m1, y1, -3)
    return (roll_date_ty(mp1, yp1), roll_date_ty(m1, y1))


