from os.path import join, exists
import sys


# OLD STYLE = SET THE ROOT_FOLDER MANUALLY
#root_folder = "/Users/michael/Dropbox/alvin/"
#root_folder = "C:\\Users\\Michael\\Dropbox\\alvin\\"
root_folder = "C:\\Users\\Trader\\Dropbox\\alvin\\"
#root_folder = "D:\\Users\\mhatmaker\\Dropbox\\alvin\\"


# NEW STYLE = CHECK FOR EXISTENCE OF VARIOUS ROOT_FOLDER VALUES
if exists("C:\\Users\\Trader\\Dropbox\\alvin\\"):
    root_folder = "C:\\Users\\Trader\\Dropbox\\alvin\\"
elif exists("D:\\Users\\mhatmaker\\Dropbox\\alvin\\"):
    root_folder = "D:\\Users\\mhatmaker\\Dropbox\\alvin\\"
elif exists("/Users/michael/Dropbox/alvin/"):
    root_folder = "/Users/michael/Dropbox/alvin/"
else:
    sys.exit("No valid root_folder found!")


python_folder = join(root_folder, "python")
args_folder = join(python_folder, "args")
data_folder = join(root_folder, "data")
raw_folder = join(data_folder, "RAW_DATA")
df_folder = join(data_folder, "DF_DATA")
html_folder = join(data_folder, "charts")
quandl_folder = join(data_folder, "DF_QUANDL")

print()
print("DATA folder:", data_folder)
print()
