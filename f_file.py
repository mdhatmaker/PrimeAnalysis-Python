import f_data_folder as folder
import json
from os import listdir
from os.path import isfile, join, split, splitext
import sys

#-----------------------------------------------------------------------------------------------------------------------

# Given a timeframe in abbreviated format (ex: '1m', '1h', 'daily')
# Return the text used by data filenames (ex: '1 Minute', '1 Hour', 'Daily')
def get_timeframe(tf):
    tfx = tf.strip().lower()
    if tfx == 'daily':
        return 'Daily'
    elif tfx == '1m':
        return '1 Minute'
    elif tfx == '1h':
        return '1 Hour'
    elif tfx == '1d':
        return '1 Day'
    else:
        return 'Unknown'
    
# Given any filename and timeframe (default is '1m')
# Return the csv filename with the appropriate timeframe appended
def get_csv_filename(filename, timeframe='1m'):
    tf = get_timeframe(timeframe)
    result = filename + ' (' + tf + ').csv'
    #print result
    return result

# Given a symbol and timeframe (default is '1m')
# Return the csv filename containing the price data (from the DF_DATA folder)
def get_df_pathname(symbol, timeframe='1m'):
    filename = get_csv_filename(symbol, timeframe)
    return join(folder.df_folder, filename)

# Given a full pathname (path/file.ext)
# Return a tuple containing (folder, filename, extension)
def split_pathname(full_pathname):
    (pathname, extension) = splitext(full_pathname)
    #(drive, path) = os.path.splitdrive(line)
    (folder, filename)  = split(pathname)
    return (folder, filename, extension)

# Given a full pathname (path/file.ext)
# Return the filename (including file extension)
def get_split_filename(full_pathname):
    (folder, filename, extension) = split_pathname(full_pathname)
    return filename + extension

# Given the pathname to a JSON file
# Return the json data from the file
def read_json(pathname):
    print("Reading JSON:", pathname)
    f = open(pathname, 'r')
    json_data = json.loads(f.read())
    f.close()
    return json_data

# Given a text string
# Return that text surrounded by quotation marks
def quoted(text, mark='"'):
    return mark + text + mark
