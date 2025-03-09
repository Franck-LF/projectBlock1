# -----------------------------------------------------
# 
#           Main Script 
# 
#   Automatically and periodically launched to:
#   - Aggregate the data from different sources
#   - Clean / format the data
# 
# -----------------------------------------------------

import numpy as np
import pandas as pd
from collections import namedtuple
from datetime import datetime
from unidecode import unidecode

pd.options.mode.copy_on_write = True


months_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
months_EN = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

# ---------------------------------------------------- #
#                                                      #
#   Functions to format data before insering into DB   #
#                                                      #
# ---------------------------------------------------- #


def string_with_comma_to_list_of_strings(st):
    ''' Convert a string such as "['string1', 'string2' ...]" into
        a list of string ['string1', 'string2', ...]

        Return: A list of strings.

        Arg:
         - st: string with the value to split.
    '''
    if pd.isna(st):
        return []
    return [item.strip() for item in st.split(",") if len(item.strip()) > 1]

def duration_to_minutes(st):
    ''' Convert duration string into number of minutes (integer)
        1h 35min   ---->    95

        Return: Integer representing the number of minutes.
        Arg:
         - st: duration string to convert.
    '''
    if pd.isna(st) or st == '': return 0
    if 'h' in st:
        a, b = st.split('h')
        if 'min' in b:
            b = b.replace('min', '')
            return 60 * int(a) + int(b.strip())
        return 60 * int(a)
    assert 'min' in st
    st = st.replace('min', '')
    return 60 * int(st)            

def unique_values_of_columns(df_data, column):
    ''' return a list with unique values found in the column,
        values in the column are like : 'value1,value2,value3' ..... 
        so we split all values in each row of the column and stack them in a list.

        Return : A list of values.

        Args:
         - df_data: dataframe with the data to extract,
         - column: string with the name of the column we want to work with.     
    '''
    df = df_data[column]
    df.dropna(inplace = True)
    df = df.apply(string_with_comma_to_list_of_strings)
    df = df.apply(pd.Series).stack().reset_index(drop=True)
    return df.unique()

def convert_months_FR_to_EN(st):
    ''' Convert french months to english months

        Return: string with a month in english.

        Arg:
         - st: string with a french date.
    '''
    if pd.isna(st): return ''
    for month_FR, month_EN in zip(months_FR, months_EN):
        if month_FR in st:
            return st.replace(month_FR, month_EN)
    print('ERROR', st)
    return st

def format_data(df):
    '''
       Converting some columns of "df" into the appropriate format:
        - correct date format,
        - duration un minutes,

        Return dataframe with formatted data.

        Args:
         - df Pandas Dataframe to be formatted,

    '''

    assert 'categories' in df.columns and 'countries' in df.columns and 'directors' in df.columns \
       and 'actors' in df.columns and 'composers' in df.columns and 'duration' in df.columns \
       and 'date' in df.columns and 'reviews' in df.columns and 'star_rating' in df.columns

    df_formated = df.copy()
    df_formated['categories'] = df_formated['categories'].apply(string_with_comma_to_list_of_strings)
    df_formated['countries'] = df_formated['countries'].apply(string_with_comma_to_list_of_strings)
    df_formated['directors'] = df_formated['directors'].apply(string_with_comma_to_list_of_strings)
    df_formated['actors'] = df_formated['actors'].apply(string_with_comma_to_list_of_strings)
    df_formated['composers'] = df_formated['composers'].apply(string_with_comma_to_list_of_strings)
    df_formated['duration'] = df_formated['duration'].apply(duration_to_minutes)
    df_formated['date'] = df_formated['date'].apply(convert_months_FR_to_EN)
    df_formated['date'] = pd.to_datetime(df_formated['date'], format='mixed')
    df_formated['notes'] = df_formated['notes'].apply(int)
    df_formated['reviews'] = df_formated['reviews'].astype(int)
    df_formated['star_rating'] = df_formated['star_rating'].apply(lambda x : float(x.replace(',', '.')))
    return df_formated





if __name__ == '__main__':

    print("--------------- Start aggregating and cleaning Data ---------------")

    now = datetime.now()
    day, month, year, hour, min, sec = now.strftime("%d-%m-%Y-%H-%M-%S").split('-')
    # print(f"Date: {year}/{month}/{day}")
    print(f"Start at: {hour}:{min}:{sec}\n")
    # day = '19'
    # month = '02'

    # Read CSV files
    df_movies = pd.read_csv(f'csv/movies_week_{year}_{month}_{day}.csv', delimiter = ',')
    df_movies_omdb = pd.read_csv(f'csv/mongoDB_week_{year}_{month}_{day}.csv', delimiter = ',')

    # Aggregate data from 2 different sources
    df_movies_omdb['summary']       = np.where(df_movies_omdb['summary'].notna(), df_movies_omdb['summary'], df_movies['summary'])
    df_movies_omdb['url_thumbnail'] = np.where(df_movies_omdb['summary'].notna(), df_movies_omdb['url_thumbnail'], df_movies['url_thumbnail'])

    # Clean data
    df_movies = format_data(df_movies)
    print(df_movies.loc[0, 'categories'], type(df_movies.loc[0, 'categories']))

    # ----------------------------------- #
    #   Save the dataframe in csv file    #
    # ----------------------------------- #
    df_movies.to_csv(f'csv/movies_week_{year}_{month}_{day}.csv', sep=',', index = False)
    df_movies_omdb.to_csv(f'csv/mongoDB_week_{year}_{month}_{day}.csv', sep=',', index = False)

    now = datetime.now()
    print(f"\nFinished aggregating and cleaning Data at: {now.strftime("%H:%M:%S")}")