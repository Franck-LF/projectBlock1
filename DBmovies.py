# --------------------------------------------------------
#
#               Data base creation
#
# --------------------------------------------------------




import math
import copy
import time
import re

import numpy as np
import pandas as pd

from tqdm import tqdm
from IPython.display import display
import mysql.connector


pd.set_option('display.max_rows', 10)
tqdm.pandas()

# --------------------------------------------------------
#
#           Create a connector on the database
#
# --------------------------------------------------------
cnx = mysql.connector.connect(user='root', password='admin', \
                              host = '127.0.0.1', database='movies')
cursor = cnx.cursor(buffered=True)





# Read the data from CSV files
df_categories = pd.read_csv('csv/categories.csv', delimiter = ',')
df_countries = pd.read_csv('csv/countries.csv', delimiter = ',')
df_movies = pd.read_csv('csv/movies_year_1980.csv', delimiter = ',')

print("Categories :", df_categories.shape)
print("Countries :", df_countries.shape)
print("movies :", df_movies.shape)







