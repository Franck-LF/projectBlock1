# -----------------------------------------------------
#
#  functions to request OMDB API
#
#
#
#
#
#
# -----------------------------------------------------



# import os
# import re
import json
import requests
from unidecode import unidecode
import numpy as np
import pandas as pd

# API KEY from "https://www.omdbapi.com/"
api_key = "b8dd5759"

pd.options.mode.copy_on_write = True

def format_string(st):
    ''' format string 
        from "title of the movie" 
        to title+of+the+movie

        Arg: st string to be converted.
    '''
    res = ''
    for c in st:
        if c.isdigit() or c.isalpha() or c.isspace():
            res += unidecode(c)
        else:
            res += ' '
    return '+'.join([word for word in res.split() if len(word) > 1])

def request_omdb_from_title(title):
    ''' Request the omdb API
    
        return a json dictionary with the information about the movie.

        Arg:
         - title: string with title of the movie we want the infos about.
    '''
    url = f"https://www.omdbapi.com/?apikey={api_key}&t={format_string(title)}"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"ERROR {title}, Response Code: {r.status_code}")
        print("Request:", url)
        return {'Response': 'False'}
    return json.loads(r.text)

def get_plot_and_thumbail_from_omdb(title):
    ''' return movie plot and thumbail through an API request.

        return: 
          - plot:      string containing the plot of the movie,
          - thumbnail: string containing the url of the thumbnail.

        Arg: title: string with the title of the movie.
    '''
    plot, thumbnail = '', ''
    res_dict = request_omdb_from_title(title)
    lst_keys = res_dict.keys()
    assert 'Response' in res_dict
    if res_dict['Response'] == 'True':
        assert 'Plot' in lst_keys and 'Poster' in lst_keys
        if res_dict['Plot'] != 'N/A':
            plot = res_dict['Plot']
        if res_dict['Poster'] != '' and res_dict['Poster'] != 'N/A':
            thumbnail = res_dict['Poster']
    return plot + "AND" + thumbnail


def request_to_OMDB(df_movies):
    ''' request OMDB API and add informations into 'df_movies'

        Return: dataframe with new informations (plot and thumbnail_url)

        Arg: df_movies Pandas Dataframe containing movie informations.
    '''
    if df_movies.empty:
        print('Dataframe is empty, nothing to request to OMDB')
        return None

    assert all(column in df_movies.columns for column in ['title', 'original_title', 'summary', 'url_thumbnail'])
    # return df_movies
    df_movies['temp']      = df_movies['original_title'].apply(get_plot_and_thumbail_from_omdb)
    df_movies['plot']      = df_movies['temp'].apply(lambda x : x.split('AND')[0])
    df_movies['thumbnail'] = df_movies['temp'].apply(lambda x : x.split('AND')[1])
    df_movies['plot']          = np.where(df_movies['plot'] != '', df_movies['plot'], df_movies['summary'])
    df_movies['url_thumbnail'] = np.where(df_movies['thumbnail'] != '', df_movies['thumbnail'], df_movies['url_thumbnail'])

    print(f"OMDB requestd for {df_movies.shape[0]} movies")
    return df_movies[['title', 'original_title', 'plot', 'url_thumbnail']]
